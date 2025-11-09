from flask.views import MethodView
from flask import request, jsonify, current_app, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..models import db, Post, Usuario, Comentario
from ..schemas.post_comment_schemas import post_schema, posts_schema
from ..decorators.auth import roles_required

api_bp = Blueprint('api', __name__, url_prefix='/api')

def is_author_or_admin(user_id, resource_owner_id, claims):
    if claims.get("role") == "admin":
        return True
    try:
        return int(user_id) == int(resource_owner_id)
    except Exception:
        return False

class PostAPI(MethodView):
    def get(self, post_id=None):
        if post_id is None:
            #posts publicados
            posts = Post.query.filter_by(is_published=True).order_by(Post.fecha_creacion.desc()).all()
            return jsonify(posts_schema.dump(posts)), 200
        else:
            post = Post.query.get_or_404(post_id)
            return jsonify(post_schema.dump(post)), 200

    @jwt_required()
    def post(self):
        data = request.get_json() or {}
        errors = post_schema.validate(data, partial=True, session=db.session)
        if errors:
            return jsonify({"error": "Validación", "detalle": errors}), 400

        #(guardamos id de usuario como string)
        user_id = get_jwt_identity()
        #campos esperados: titulo, contenido, categoria_id, is_published opcional
        titulo = data.get("titulo")
        contenido = data.get("contenido")
        categoria_id = data.get("categoria_id")
        is_published = data.get("is_published", True)

        if not titulo or not contenido or not categoria_id:
            return jsonify({"error": "titulo, contenido y categoria_id son obligatorios"}), 400

        nuevo = Post(
            titulo=titulo,
            contenido=contenido,
            categoria_id=categoria_id,
            autor_id=int(user_id),
            is_published=bool(is_published)
        )
        try:
            db.session.add(nuevo)
            db.session.commit()
            return jsonify(post_schema.dump(nuevo)), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error guardando post", "detalle": str(e)}), 500

    @jwt_required()
    def put(self, post_id):
        post = Post.query.get_or_404(post_id)
        user_id = get_jwt_identity()
        claims = get_jwt()
        if not is_author_or_admin(user_id, post.autor_id, claims):
            return jsonify({"error": "No autorizado"}), 403

        data = request.get_json() or {}
        errors = post_schema.validate(data, partial=True)
        if errors:
            return jsonify({"error": "Validación", "detalle": errors}), 400

        for field in ("titulo", "contenido", "categoria_id", "is_published"):
            if field in data:
                setattr(post, field, data[field])
        try:
            db.session.commit()
            return jsonify(post_schema.dump(post)), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error actualizando", "detalle": str(e)}), 500

    @jwt_required()
    def delete(self, post_id):
        post = Post.query.get_or_404(post_id)
        user_id = get_jwt_identity()
        claims = get_jwt()
        if not is_author_or_admin(user_id, post.autor_id, claims):
            return jsonify({"error": "No autorizado"}), 403
        try:
            db.session.delete(post)
            db.session.commit()
            return jsonify({"mensaje": "Post eliminado"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error eliminando", "detalle": str(e)}), 500

post_view = PostAPI.as_view('posts_api')
api_bp.add_url_rule('/posts', defaults={'post_id': None}, view_func=post_view, methods=['GET'])
api_bp.add_url_rule('/posts', view_func=post_view, methods=['POST'])
api_bp.add_url_rule('/posts/<int:post_id>', view_func=post_view, methods=['GET', 'PUT', 'DELETE'])


@api_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@roles_required(["admin", "moderator"])
def delete_comment(comment_id):
    comentario = Comentario.query.get(comment_id)
    if not comentario:
        return jsonify({"error": "Comentario no encontrado"}), 404

    usuario_id = get_jwt_identity()
    claims = get_jwt()

    if comentario.autor_id != int(usuario_id) and claims.get("role") not in ["admin", "moderator"]:
        return jsonify({"error": "No tienes permiso para eliminar este comentario"}), 403

    db.session.delete(comentario)
    db.session.commit()

    return "", 204