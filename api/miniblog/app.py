from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from datetime import timedelta
from .extensions import db, ma
from .models import Usuario
from .views.main_views import main_bp
from .views.auth_views import auth_bp
from .views.user_views import user_bp
from .views.posts_api import api_bp
from .views.categories_views import categories_bp
try:
    from .models import Usuario
    from .extensions import db, ma
except ImportError: 
    print("Error: No se pudieron importar 'db', 'ma' o 'Usuario'.")
    print("Asegúrate de haber movido 'models.py' a 'models/__init__.py'")
    print("y de haber movido 'schemas.py' a 'schemas/user_schemas.py' (e importado 'ma' en 'schemas/__init__.py')")

try:
    from .views.main_views import main_bp
    from .views.auth_views import auth_bp
    from .views.user_views import user_bp
    from .views.posts_api import api_bp 
    
except ImportError as e:
    print(f"Error importando Blueprints: {e}")
    print("Asegúrate de que tus archivos en la carpeta /views (main_views.py, auth_views.py, etc.) existan y definan un Blueprint.")


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "cualquier-cosa"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://miniblog_user:Tomo@localhost/miniblog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "demo" # Renombrado de 'app.secret_key'

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
ma.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app) 
login_manager.login_view = 'auth_views.login' 


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


app.register_blueprint(main_bp)       # Rutas de templates (/, /post/<id>, etc.)
app.register_blueprint(auth_bp)       # Rutas de Auth (/login, /api/login, etc.)
app.register_blueprint(user_bp)       # Rutas de User API (/api/users)
app.register_blueprint(api_bp)        # Rutas de Post/Comment API (/api/posts, /api/comments)
app.register_blueprint(categories_bp) # Rutas de Category API (/api/categories)


def init_db():
    with app.app_context():
        from .models import Usuario, Post, Comentario, Categoria, UserCredentials
        db.create_all()
        
        categorias_a_crear = ['Tecnología', 'Viajes', 'General', 'Cocina', 'Deportes', 'Cine', 'Música']
        for nombre_cat in categorias_a_crear:
            existe = Categoria.query.filter_by(nombre=nombre_cat).first()
            if not existe:
                nueva_cat = Categoria(nombre=nombre_cat)
                db.session.add(nueva_cat)
        
        db.session.commit()

#with app.app_context():
    #init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
