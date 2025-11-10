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