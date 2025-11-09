from flask import (
    Blueprint, render_template, request, 
    redirect, url_for, flash
)
from flask_login import login_required, current_user

from ..schemas import user_schema
from ..models import db, Post, Comentario, Categoria, Usuario

# 1. Creamos el Blueprint. Lo llamaremos 'main'.
main_bp = Blueprint('main', __name__)


# 2. Cambiamos todos los @app.route por @main_bp.route
@main_bp.route('/')
def index():
    posts = Post.query.order_by(Post.fecha_creacion.desc()).all()
    return render_template('index.html', posts=posts)


@main_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required 
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        texto_comentario = request.form.get('texto_comentario')
        
        if texto_comentario and current_user.is_authenticated:
            nuevo_comentario = Comentario(
                texto=texto_comentario,
                autor_id=current_user.id,
                post_id=post.id)
            db.session.add(nuevo_comentario)
            db.session.commit()
            flash('¡Comentario añadido con éxito!', 'success')
            
            # 3. Actualizamos url_for() para usar el Blueprint
            return redirect(url_for('main.post_detail', post_id=post.id))
        else:
            flash('El autor y el texto del comentario son obligatorios.', 'danger')

    return render_template('post_detail.html', post=post)


@main_bp.route('/create_post', methods=['GET', 'POST'])
@login_required 
def create_post():
    if request.method == 'POST':
        titulo = request.form.get('title')
        contenido = request.form.get('content')
        autor_id = request.form.get('autor_id') # Tu lógica original
        categoria_id = request.form.get('categoria_id')
        
        if titulo and contenido and autor_id:
            nuevo_post = Post(titulo=titulo, contenido=contenido, autor_id=autor_id, categoria_id=categoria_id)
            db.session.add(nuevo_post)
            db.session.commit()

            flash('¡Post creado con éxito!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Título, contenido y autor son campos obligatorios.', 'danger')
            return redirect(url_for('main.create_post'))

    usuarios = Usuario.query.all()
    categorias = Categoria.query.all()
    return render_template('create_post.html', users=usuarios, categorias=categorias)


@main_bp.route('/category/<int:category_id>')
def posts_by_category(category_id):
    categoria = Categoria.query.get_or_404(category_id)
    return render_template('posts_by_category.html', category=categoria)


@main_bp.context_processor
def inject_categories():
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return dict(all_categories=categorias)