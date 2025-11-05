# --- 1. IMPORTACIONES ---
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario, Post, Comentario, Categoria, UserCredentials
from flask_jwt_extended import create_access_token, JWTManager
from datetime import timedelta
from schemas import ma, user_schema, users_schema
from verif_admin import roles_required

# --- 2. CONFIGURACIÓN ---
app = Flask(__name__)

# Configuración de la base de datos
app.config["JWT_SECRET_KEY"] = "cualquier-cosa"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Anabella2025!@localhost/miniblog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "demo" # Clave para los mensajes flash

# Inicializa el gestor de JWT

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
ma.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)  # ¡Añade esta línea!
login_manager.login_view = 'login' # Define la ruta de login

def init_db():
    with app.app_context():
        db.create_all()
        
        # Verificar y crear categorías si no existen
        categorias_a_crear = ['Tecnología', 'Viajes', 'General', 'Cocina', 'Deportes', 'Cine', 'Música']
        for nombre_cat in categorias_a_crear:
            existe = Categoria.query.filter_by(nombre=nombre_cat).first()
            if not existe:
                nueva_cat = Categoria(nombre=nombre_cat)
                db.session.add(nueva_cat)
        
        db.session.commit()

# Inicialización de la base de datos y migraciones
with app.app_context():
    init_db()

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
    posts = Post.query.order_by(Post.fecha_creacion.desc()).all()
    return render_template('index.html', posts=posts)


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Faltan username o password"}), 400

    user = Usuario.query.filter_by(nombre=username).first()

    if not user or not user.credentials or not check_password_hash(
        pwhash=user.credentials.password_hash, 
        password=password
    ):
        return jsonify({"error": "Credenciales inválidas"}), 401

    # En lugar de login_user(user), creo el token:
    
    access_token = create_access_token(identity=str(user.id))
    
    # Retorno el token 
    return jsonify({
        "mensaje": "Login exitoso",
        "token": access_token,
        "user": user_schema.dump(user) 
    }), 200

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))

#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         user = Usuario.query.filter_by(nombre=username).first()
#         # Verificamos si el usuario existe y si la contraseña es correcta
#         if user and user.credentials and check_password_hash(
#             pwhash=user.credentials.password_hash, 
#             password=password
#         ):
#             login_user(user) # Iniciamos la sesión para el usuario
#             next_page = request.args.get('next') 
#             return redirect(next_page or url_for('index'))
#         else: 
#             flash('Usuario o contraseña inválidos.', 'danger')
            
#     return render_template('login.html')

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # 2.2. Validar que los datos existan
    if not username or not email or not password:
        return jsonify({"error": "Faltan datos (username, email o password)"}), 400

    # 2.3. Validar email único (Checklist)
    existing_user = Usuario.query.filter_by(correo=email).first()
    if existing_user:
        return jsonify({"error": "El email ya está registrado"}), 409

    # 3.1. Hashear la contraseña por seguridad
    hashed_password = generate_password_hash(password)

    # 3.2. Crear el nuevo Usuario Y sus Credenciales
    try:
        # 1. Crea el Usuario (SIN contraseña)
        new_user = Usuario(
            nombre=username,
            correo=email
        )
        
        # 2. Crea las Credenciales y las enlaza al usuario
        new_credentials = UserCredentials(
            password_hash=hashed_password,
            user=new_user  # <-- ¡La magia de SQLAlchemy enlaza el ID!
        )

        # 3. Añade AMBOS a la sesión
        db.session.add(new_user)
        db.session.add(new_credentials)
        
        # 4. ¡Guarda todo en la base de datos!
        db.session.commit()

    except Exception as e:
        db.session.rollback() # Deshacer cambios si algo falla
        return jsonify({"error": "Error al guardar en la base de datos", "detalle": str(e)}), 500

    # 3.5. Responder con éxito
    # (¡OJO! Tu modelo usa 'nombre' y 'correo', no 'username' y 'email')
    return jsonify({
        "mensaje": "Usuario registrado exitosamente",
        "usuario": {
            "id": new_user.id,
            "username": new_user.nombre, 
            "email": new_user.correo        
        }
    }), 201

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         email = request.form.get('email')
#         password = request.form.get('password')
        
#         user_existente = Usuario.query.filter_by(nombre=username).first()
#         if user_existente:
#             flash('El nombre de usuario ya existe.', 'danger')
#             return redirect(url_for('register'))
            
#         hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
#         nuevo_usuario = Usuario(nombre=username, correo=email, contrasena=hashed_password)
#         print(f"Usuario: {username}, Contraseña ingresada: {password}, Hash en DB: {hashed_password}")

#         db.session.add(nuevo_usuario)
#         db.session.commit()
#         flash('¡Registro exitoso! Por favor, inicia sesión.', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('index'))


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
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
            return redirect(url_for('post_detail', post_id=post.id))
        else:
            flash('El autor y el texto del comentario son obligatorios.', 'danger')

    return render_template('post_detail.html', post=post)

@app.route('/create_post', methods=['GET', 'POST'])
@login_required 
def create_post():
    if request.method == 'POST':
        titulo = request.form.get('title')
        contenido = request.form.get('content')
        autor_id = request.form.get('autor_id')
        categoria_id = request.form.get('categoria_id')
        if titulo and contenido and autor_id:
            nuevo_post = Post(titulo=titulo, contenido=contenido, autor_id=autor_id, categoria_id=categoria_id)
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

@app.route('/api/users', methods=['GET'])
@roles_required(roles=['admin'])
def get_all_users(): # Obtiene una lista de todos los usuarios (Solo Admin)
    try:
        users = Usuario.query.all()
        
        return jsonify(users_schema.dump(users)), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener usuarios", "detalle": str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['GET', 'PATCH', 'DELETE'])
@roles_required(roles=['admin'])
def handle_user(user_id): # Gestiona un usuario específico por ID (Solo Admin)
    user = Usuario.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    #  GET 
    if request.method == 'GET':
        # Usamos 'user_schema' (singular) para serializar
        return jsonify(user_schema.dump(user)), 200

    # PATCH 
    elif request.method == 'PATCH':
        data = request.get_json()

        # Un admin puede cambiar el 'role' o 'is_active' de otro usuario
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']

        try:
            db.session.commit()
            return jsonify({"mensaje": "Usuario actualizado", "user": user_schema.dump(user)}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al actualizar usuario", "detalle": str(e)}), 500

    #  DELETE 
    elif request.method == 'DELETE':
        try:
            # OJO: Borrar un usuario puede dar error si tiene posts/comentarios
            # (Depende de cómo esté configurada tu BD con 'on delete')
            db.session.delete(user)
            db.session.commit()
            return jsonify({"mensaje": f"Usuario con id {user_id} eliminado"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al eliminar usuario", "detalle": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
