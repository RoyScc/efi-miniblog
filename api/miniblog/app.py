# --- 1. IMPORTACIONES ---
# Importo todo lo que necesito para que la aplicación funcione.
# Flask para la app, render_template para las vistas, y el resto para manejar formularios y la base de datos.
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from models import db, Usuario, Post, Comentario, Categoria

# --- 2. CONFIGURACIÓN ---
# Creo la instancia de la aplicación Flask.
app = Flask(__name__)

# Configuro la conexión a mi base de datos MySQL en XAMPP.
# La base de datos se llama 'miniblog_db' y el usuario es 'root' sin contraseña.
app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql+pymysql://root:demo@localhost/miniblog')
app.secret_key = "demo"

# Inicializo las extensiones, vinculándolas con mi app.
db.init_app(app)
migrate = Migrate(app, db)


# --- 4. CONTEXT PROCESSOR ---
# Esta función hace que la lista de todas las categorías ('all_categories')
# esté disponible en todas mis plantillas HTML sin tener que pasarla en cada 'render_template'.
@app.context_processor
def inject_categories():
    categories = Categoria.query.order_by(Categoria.nombre).all()
    return dict(all_categories=categories)


# --- 5. RUTAS Y VISTAS ---
# Defino las diferentes páginas (URLs) de mi aplicación.

# Ruta para la página principal.
@app.route('/')
def index():
    # Busco todos los posts en la base de datos, ordenados del más nuevo al más viejo.
    posts = Post.query.order_by(Post.fecha_creacion.desc()).all()
    # Muestro la plantilla 'index.html' y le paso la lista de posts.
    return render_template('index.html', posts=posts)

# Ruta para ver un post en detalle.
@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    # Busco el post por su ID. Si no lo encuentra, da un error 404.
    post = Post.query.get_or_404(post_id)
    
    # Si el usuario envía el formulario de comentario (método POST)...
    if request.method == 'POST':
        comment_text = request.form.get('comment_text')
        user_id = request.form.get('user_id')
        
        # Creo el nuevo comentario y lo guardo en la base de datos.
        new_comment = Comentario(text=comment_text, user_id=user_id, post_id=post.id)
        db.session.add(new_comment)
        db.session.commit()
        flash('¡Comentario añadido con éxito!', 'success')
        # Redirijo a la misma página para que se vea el nuevo comentario.
        return redirect(url_for('post_detail', post_id=post.id))

    # Si es una visita normal (método GET), muestro la plantilla con los datos del post.
    users = Usuario.query.all() # Necesito la lista de usuarios para el formulario.
    return render_template('post_detail.html', post=post, users=users)

# Ruta para la página de creación de posts.
@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    # Si el usuario envía el formulario...
    if request.method == 'POST':
        # Obtengo los datos del formulario.
        title = request.form.get('title')
        content = request.form.get('content')
        autor_id = request.form.get('autor_id')
        category_ids = request.form.getlist('categories')

        # Creo el nuevo post.
        new_post = Post(titulo=title, contenido=content, autor_id=autor_id)
        
        # Le asigno las categorías que se seleccionaron.
        for cat_id in category_ids:
            category = Categoria.query.get(cat_id)
            if category:
                new_post.categorias.append(category)

        # Guardo el post en la base de datos y muestro un mensaje.
        db.session.add(new_post)
        db.session.commit()
        flash('¡Post creado con éxito!', 'success')
        return redirect(url_for('index'))

    # Si es una visita normal, muestro el formulario de creación.
    users = Usuario.query.all()
    categorias = Categoria.query.all()
    return render_template('create_post.html', users=users, categorias=categorias)

# Ruta para ver los posts de una categoría específica.
@app.route('/category/<int:category_id>')
def posts_by_category(category_id):
    category = Categoria.query.get_or_404(category_id)
    # Muestro una plantilla pasándole la categoría y sus posts asociados.
    return render_template('posts_by_category.html', category=category)


if __name__ == '__main__':
    app.run(debug=True)
