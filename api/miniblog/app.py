from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask import jsonify
from datetime import timedelta
from .extensions import db, ma
from .models import Usuario
from .views.main_views import main_bp
from .views.auth_views import auth_bp
from .views.user_views import user_bp
from .views.posts_api import api_bp
from .views.categories_views import categories_bp
from .views.stats_views import stats_bp


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "cualquier-cosa"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:gisel123@localhost/miniblog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "demo" 

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
ma.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app) 
login_manager.login_view = None

@login_manager.unauthorized_handler
def unauthorized_callback():
    return jsonify({"error": "No autenticado"}), 401

CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

app.register_blueprint(main_bp)      
app.register_blueprint(auth_bp)       
app.register_blueprint(user_bp)       
app.register_blueprint(api_bp)        
app.register_blueprint(categories_bp) 
app.register_blueprint(stats_bp)

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

if __name__ == '__main__':
    app.run(debug=True, port=5001)
