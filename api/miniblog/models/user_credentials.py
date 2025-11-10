from ..extensions import db

class UserCredentials(db.Model):
    __tablename__ = 'user_credentials'
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, unique=True)
    user = db.relationship('Usuario', backref=db.backref('credentials', uselist=False))

    def __str__(self):
        return f'<Credenciales para Usuario ID: {self.user_id}>'