from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
db = SQLAlchemy()

class Usuario(db.Model, UserMixin): # Usuarios registrados en el miniblog
    __tablename__ = 'usuarios'

    id =  db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(64),  unique=True, nullable=False)
    correo = db.Column(db.String(120),  unique=True, nullable=False)
    contrasena = db.Column(db.String(256), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    posts = db.relationship('Post', backref='autor', lazy=True)
    comentarios = db.relationship('Comentario', backref='autor', lazy=True)

    def __str__(self):
        return f'<Usuario: {self.name}>'
    

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con Usuario (autor del post)
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # Relación con Comentarios
    comentarios = db.relationship('Comentario', backref='post', lazy=True)
    
    

class Comentario(db.Model):
    __tablename__ = 'comentarios'

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con modelo Usuario
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # Relación con Post (comentado)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    def __repr__(self):
        return f'<Comentario {self.id}>'
    
class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'


