from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Usuario

def roles_required(roles=[]):
    # verifica el rol del usuario DESDE UN JWT.
    def decorator(fn):
        @wraps(fn)
        @jwt_required() # Asegura que el JWT es válido
        def wrapper(*args, **kwargs):
            
            # Obtiene el ID del usuario (el 'sub') de adentro del token
            current_user_id = get_jwt_identity()
            
            # Busca al usuario en la BD con ese ID
            user = Usuario.query.get(current_user_id)
            
            # Sin current_user
            if not user or user.role not in roles:
                return jsonify({"error": "Acceso no autorizado. Se requiere rol de administrador."}), 403
            
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

admin_required = roles_required(roles=['admin'])
mod_required = roles_required(roles=['admin', 'mod'])
user_required = roles_required(roles=['user', 'mod', 'admin'])