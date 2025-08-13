# --- 1. IMPORTACIONES ---
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from models import db, Usuario, Post, Comentario, Categoria
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)

# --- 2. CONFIGURACIÓN ---
app = Flask(__name__)

# Configuración de la base de datos (SIN contraseña para 'root')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/miniblog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "demo" # Clave para los mensajes flash

# Inicialización de la base de datos y migraciones
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)  # ¡Añade esta línea!
login_manager.login_view = 'login' # Define la ruta de login

# --- Agrega esta función para que LoginManager sepa cómo encontrar a los usuarios ---
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
# Pone la lista de categorías disponible en todas las plantillas.
@app.context_processor
def inject_categories():
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return dict(all_categories=categorias)


# --- 4. RUTAS Y VISTAS ---

@app.route('/')
def index():
    #posts = Post.query.order_by(Post.fecha_creacion.desc()).all()
    return render_template('index.html')


# app.py

# ... (tus imports y configuraciones) ...

@app.route('/login')
def login():
    # Renderiza un formulario de login.html
    return render_template('login.html')
@app.route('/register')
def register():
    # Renderiza un formulario de login.html
    return render_template('register.html')
# ... (tus otras rutas) ...


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        texto_comentario = request.form.get('texto_comentario')
        autor_id = request.form.get('autor_id')
        if texto_comentario and autor_id:
            nuevo_comentario = Comentario(texto=texto_comentario, autor_id=autor_id, post_id=post.id)
            db.session.add(nuevo_comentario)
            db.session.commit()
            flash('¡Comentario añadido con éxito!', 'success')
        else:
            flash('El autor y el texto del comentario son obligatorios.', 'danger')
        return redirect(url_for('post_detail', post_id=post.id))
    usuarios = Usuario.query.all()
    return render_template('post_detail.html', post=post, users=usuarios)

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        titulo = request.form.get('title')
        contenido = request.form.get('content')
        autor_id = request.form.get('autor_id')
        ids_categorias = request.form.getlist('categories')
        if titulo and contenido and autor_id:
            nuevo_post = Post(titulo=titulo, contenido=contenido, autor_id=autor_id)
            for cat_id in ids_categorias:
                categoria = Categoria.query.get(cat_id)
                if categoria:
                    nuevo_post.categorias.append(categoria)
            db.session.add(nuevo_post)
            db.session.commit()
            flash('¡Post creado con éxito!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Título, contenido y autor son campos obligatorios.', 'danger')
            return redirect(url_for('create_post'))
    usuarios = Usuario.query.all()
    categorias = Categoria.query.all()
    return render_template('create_post.html', users=usuarios, categorias=categorias)

@app.route('/category/<int:category_id>')
def posts_by_category(category_id):
    categoria = Categoria.query.get_or_404(category_id)
    return render_template('posts_by_category.html', category=categoria)

# --- RUTA PARA CREAR DATOS INICIALES ---
@app.route('/init')
def init_data():
    # --- USUARIOS ---
    if Usuario.query.count() == 0:
        usuario1 = Usuario(nombre_usuario='valentina', correo='val@mail.com', contrasena='123')
        usuario2 = Usuario(nombre_usuario='invitado', correo='invitado@mail.com', contrasena='123')
        db.session.add(usuario1)
        db.session.add(usuario2)
    
    # --- CATEGORÍAS ---
    categorias_a_crear = ['Tecnología', 'Viajes', 'General', 'Cocina', 'Deportes', 'Cine', 'Música']
    for nombre_cat in categorias_a_crear:
        existe = Categoria.query.filter_by(nombre=nombre_cat).first()
        if not existe:
            nueva_cat = Categoria(nombre=nombre_cat)
            db.session.add(nueva_cat)

    db.session.commit()
    flash('¡Datos iniciales verificados y creados con éxito!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
