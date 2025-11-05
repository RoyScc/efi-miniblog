from app import app
from models import Post, Comentario
from schemas.post_comment_schemas import post_schema, comment_schema

with app.app_context():
    
    post = Post(titulo="Test", contenido="probando ando", autor_id=1, categoria_id=1)
    print("Serialización Post:", post_schema.dump(post))

    
    comment = Comentario(texto="probando 12223 ana", autor_id=1, post_id=1)
    print("Serialización Comentario:", comment_schema.dump(comment))
