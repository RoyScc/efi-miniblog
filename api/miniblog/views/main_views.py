from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..schemas import user_schema, post_schema, posts_schema
from ..models import db, Post, Comentario, Categoria, Usuario

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Ruta de prueba para la API.
    Devuelve todos los posts en JSON.
    """
    posts = Post.query.order_by(Post.fecha_creacion.desc()).all()
    return jsonify(posts_schema.dump(posts)), 200


@main_bp.route('/posts/<int:post_id>', methods=['GET', 'POST'])
@jwt_required()
def post_detail(post_id):
    """
    Obtener detalle de un post o agregar comentario.
    """
    post = Post.query.get_or_404(post_id)
    user_id = get_jwt_identity()

    if request.method == 'POST':
        data = request.get_json() or {}
        texto_comentario = data.get('texto_comentario')

        if texto_comentario:
            nuevo_comentario = Comentario(
                texto=texto_comentario,
                autor_id=user_id,
                post_id=post.id
            )
            db.session.add(nuevo_comentario)
            db.session.commit()
            return jsonify({
                "mensaje": "Comentario añadido con éxito",
                "comentario": {
                    "id": nuevo_comentario.id,
                    "texto": nuevo_comentario.texto,
                    "autor_id": nuevo_comentario.autor_id,
                    "post_id": nuevo_comentario.post_id
                }
            }), 201
        else:
            return jsonify({"error": "El texto del comentario es obligatorio"}), 400

    return jsonify(post_schema.dump(post)), 200


@main_bp.route('/create_post', methods=['POST'])
@jwt_required()
def create_post():
    """
    Crear un nuevo post desde JSON.
    """
    data = request.get_json() or {}
    titulo = data.get('title')
    contenido = data.get('content')
    categoria_id = data.get('categoria_id')
    user_id = get_jwt_identity()

    if not titulo or not contenido:
        return jsonify({"error": "Título y contenido son campos obligatorios"}), 400

    nuevo_post = Post(
        titulo=titulo,
        contenido=contenido,
        autor_id=user_id,
        categoria_id=categoria_id
    )
    db.session.add(nuevo_post)
    db.session.commit()

    return jsonify(post_schema.dump(nuevo_post)), 201


@main_bp.route('/api/posts/<int:post_id>/reviews', methods=['GET', 'POST'])
def post_reviews(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        from flask_jwt_extended import jwt_required, get_jwt_identity

        @jwt_required()
        def protected_create():
            data = request.get_json() or {}
            texto = data.get('texto')
            user_id = get_jwt_identity()

            if not texto:
                return jsonify({"error": "Texto de review obligatorio"}), 400

            review = Comentario(
                texto=texto,
                autor_id=user_id,
                post_id=post.id
            )
            db.session.add(review)
            db.session.commit()

            return jsonify({
                "id": review.id,
                "texto": review.texto,
                "autor_id": review.autor_id,
                "post_id": review.post_id
            }), 201

        return protected_create()

    reviews = Comentario.query.filter_by(post_id=post.id, is_visible=True).all()
    return jsonify([
        {
            "id": r.id,
            "texto": r.texto,
            "autor_id": r.autor_id
        }
        for r in reviews
    ]), 200



@main_bp.route('/category/<int:category_id>')
def posts_by_category(category_id):
    """
    Obtener posts filtrados por categoría.
    """
    categoria = Categoria.query.get_or_404(category_id)
    posts = Post.query.filter_by(categoria_id=categoria.id).order_by(Post.fecha_creacion.desc()).all()
    return jsonify({
        "categoria": {"id": categoria.id, "nombre": categoria.nombre},
        "posts": posts_schema.dump(posts)
    }), 200


@main_bp.route('/api/reviews/<int:review_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
@jwt_required()
def review_detail(review_id):
    review = Comentario.query.get_or_404(review_id)

    if request.method == "OPTIONS":
        return '', 200

    if request.method == "PUT":
        try:
            user_id = int(get_jwt_identity())
        except ValueError:
            return jsonify({"error": "Identidad de usuario inválida en el token"}), 401
            
        if user_id != review.autor_id:
            return jsonify({"error": "No autorizado"}), 403

        data = request.get_json() or {}
        texto = data.get("texto")

        if not texto:
            return jsonify({"error": "Texto obligatorio"}), 400

        review.texto = texto
        db.session.commit()

        return jsonify({
            "id": review.id,
            "texto": review.texto,
            "autor_id": review.autor_id,
            "post_id": review.post_id
        }), 200

    if request.method == "DELETE":
        try:
            user_id = int(get_jwt_identity())
        except ValueError:
            return jsonify({"error": "Identidad de usuario inválida en el token"}), 401

        if user_id != review.autor_id:
            return jsonify({"error": "No autorizado"}), 403

        db.session.delete(review)
        db.session.commit()

        return jsonify({"mensaje": "Review eliminada"}), 200
    
    if request.method == "GET":
        return jsonify({
            "id": review.id,
            "texto": review.texto,
            "autor_id": review.autor_id,
            "post_id": review.post_id
        }), 200