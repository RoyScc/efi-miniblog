from app import app
from models import Post

with app.app_context():
    post = Post.query.filter_by(titulo="Prueba Tarea 7").first()
    if post:
        print("Post encontrado:")
        print(post.__dict__)  
    else:
        print("No se encontró el post.")
