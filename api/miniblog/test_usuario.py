# test_usuario.py
from app import app, db
from models import Usuario
from datetime import datetime

with app.app_context():
    # Verificar si ya existe el usuario "Admin"
    usuario_existente = Usuario.query.filter_by(nombre="Admin").first()
    
    if not usuario_existente:
        # Crear el usuario si no existe
        usuario = Usuario(
            nombre="Admin",
            correo="admin@example.com",
            activo=True,
            role="admin",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(usuario)
        db.session.commit()
        print("Usuario 'Admin' creado exitosamente.")
    else:
        print("El usuario 'Admin' ya existe:", usuario_existente.nombre)

    # Mostrar todos los usuarios
    usuarios = Usuario.query.all()
    print("Usuarios en la base de datos:")
    for u in usuarios:
        print(f"- {u.id}: {u.nombre} ({u.correo})")

