from app import app, db
from models import Post, Usuario, Categoria
from datetime import datetime

with app.app_context():
    usuario = Usuario.query.first()
    categoria = Categoria.query.first()

    if not usuario:
        print("No hay usuarios en la base de datos. Primero crea uno con test_usuario.py")
    elif not categoria:
        print("No hay categorías en la base de datos. Crea al menos una categoría primero.")
    else:
        
        titulo_post = "Prueba Tarea 7"
        post_existente = Post.query.filter_by(titulo=titulo_post).first()

        if post_existente:
            print(f"El post '{titulo_post}' ya existe: {post_existente.id}")
        else:
            
            nuevo_post = Post(
                titulo=titulo_post,
                contenido="Contenido de prueba",
                is_published=True,
                updated_at=datetime.utcnow(),
                autor_id=usuario.id,
                categoria_id=categoria.id
            )
            db.session.add(nuevo_post)
            db.session.commit()
            print(f"Post creado correctamente: {nuevo_post.id}")
