# --- 1. IMPORTACIONES ---
# Importo todo lo que necesito para que la aplicación funcione.
# Flask para la app, render_template para las vistas, y el resto para manejar formularios y la base de datos.
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

# --- 2. CONFIGURACIÓN ---
# Creo la instancia de la aplicación Flask.
app = Flask(__name__)

# Configuro la conexión a mi base de datos MySQL en XAMPP.
# La base de datos se llama 'miniblog_db' y el usuario es 'root' sin contraseña.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/miniblog_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Configuración recomendada.
app.config['SECRET_KEY'] = 'mi_clave_secreta_para_efi' # Clave para los mensajes flash.

# Inicializo las extensiones, vinculándolas con mi app.
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# --- 3. MODELOS DE LA BASE DE DATOS ---
# Defino la estructura de mis tablas usando clases de Python.

# Tabla de asociación para la relación muchos-a-muchos entre Post y Category.
# Un post puede tener varias categorías y viceversa.
post_category = db.Table('post_category',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

# Modelo para la tabla de Usuarios.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False) # En un proyecto real, esto debería estar hasheado.
    
    # Relaciones: Un usuario puede tener muchos posts y muchos comentarios.
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

# Modelo para la tabla de Posts (Entradas).
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Clave foránea para saber qué usuario escribió el post.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relaciones: Un post puede tener muchos comentarios y muchas categorías.
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    categories = db.relationship('Category', secondary=post_category, lazy='subquery',
        backref=db.backref('posts', lazy=True))

# Modelo para la tabla de Comentarios.
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Claves foráneas para vincular el comentario a un usuario y a un post.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

# Modelo para la tabla de Categorías.
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


# --- 4. CONTEXT PROCESSOR ---
# Esta función hace que la lista de todas las categorías ('all_categories')
# esté disponible en todas mis plantillas HTML sin tener que pasarla en cada 'render_template'.
@app.context_processor
def inject_categories():
    categories = Category.query.order_by(Category.name).all()
    return dict(all_categories=categories)


# --- 5. RUTAS Y VISTAS ---
# Defino las diferentes páginas (URLs) de mi aplicación.

# Ruta para la página principal.
@app.route('/')
def index():
    # Busco todos los posts en la base de datos, ordenados del más nuevo al más viejo.
    posts = Post.query.order_by(Post.created_at.desc()).all()
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
        new_comment = Comment(text=comment_text, user_id=user_id, post_id=post.id)
        db.session.add(new_comment)
        db.session.commit()
        flash('¡Comentario añadido con éxito!', 'success')
        # Redirijo a la misma página para que se vea el nuevo comentario.
        return redirect(url_for('post_detail', post_id=post.id))

    # Si es una visita normal (método GET), muestro la plantilla con los datos del post.
    users = User.query.all() # Necesito la lista de usuarios para el formulario.
    return render_template('post_detail.html', post=post, users=users)

# Ruta para la página de creación de posts.
@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    # Si el usuario envía el formulario...
    if request.method == 'POST':
        # Obtengo los datos del formulario.
        title = request.form.get('title')
        content = request.form.get('content')
        user_id = request.form.get('user_id')
        category_ids = request.form.getlist('categories')

        # Creo el nuevo post.
        new_post = Post(title=title, content=content, user_id=user_id)
        
        # Le asigno las categorías que se seleccionaron.
        for cat_id in category_ids:
            category = Category.query.get(cat_id)
            if category:
                new_post.categories.append(category)

        # Guardo el post en la base de datos y muestro un mensaje.
        db.session.add(new_post)
        db.session.commit()
        flash('¡Post creado con éxito!', 'success')
        return redirect(url_for('index'))

    # Si es una visita normal, muestro el formulario de creación.
    users = User.query.all()
    categories = Category.query.all()
    return render_template('create_post.html', users=users, categories=categories)

# Ruta para ver los posts de una categoría específica.
@app.route('/category/<int:category_id>')
def posts_by_category(category_id):
    category = Category.query.get_or_404(category_id)
    # Muestro una plantilla pasándole la categoría y sus posts asociados.
    return render_template('posts_by_category.html', category=category)


# --- 6. EJECUCIÓN DE LA APP ---
# Esta parte solo se ejecuta si corro el archivo directamente (python app.py).
if __name__ == '__main__':
    # Inicia el servidor de desarrollo de Flask en modo debug.
    app.run(debug=True)
