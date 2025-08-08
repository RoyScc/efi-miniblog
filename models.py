from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model): # Usuarios registrados en el miniblog
    __tablename__ = 'usuarios'

    id =  db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64),  unique=True, nullable=False)
    email = db.Column(db.String(120),  unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __str__(self):
        return f'<Usuario: {self.name}>'

