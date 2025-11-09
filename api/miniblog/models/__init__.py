from ..extensions import db

from flask_login import UserMixin
from datetime import datetime, timezone

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id =  db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(64),  unique=True, nullable=False)
    correo = db.Column(db.String(120),  unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), nullable=False, default='user')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    posts = db.relationship('Post', backref='autor', lazy=True)
    comentarios = db.relationship('Comentario', backref='autor', lazy=True)
    
    def __str__(self):
        return f'<Usuario: {self.nombre}>'

class UserCredentials(db.Model):
    __tablename__ = 'user_credentials'
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, unique=True)
    user = db.relationship('Usuario', backref=db.backref('credentials', uselist=False))

    def __str__(self):
        return f'<Credenciales para Usuario ID: {self.user_id}>'

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc)
    )
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    comentarios = db.relationship('Comentario', backref='post', lazy=True)

    is_published = db.Column(db.Boolean, default=True) 

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc)
    )
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    def __repr__(self):
        return f'<Comentario {self.id}>'
    
class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    posts = db.relationship('Post', backref='categoria', lazy=True)
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'