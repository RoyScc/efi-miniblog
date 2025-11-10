from ..extensions import db
from datetime import datetime, timezone

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