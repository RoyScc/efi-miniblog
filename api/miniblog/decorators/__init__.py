
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt
from flask_login import current_user


# decorador generico de roles

def roles_required(*roles):
    """
    Controla el acceso al endpoint. Solo permite el paso si el rol del usuario
    en el token JWT se encuentra en la lista de roles permitidos (*roles).
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()  # Asegura que el token sea válido
        def decorator(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get("role") #Obtiene rol del token
            
            # Comparar con roles permitidos
            if user_role in roles:
                return fn(*args, **kwargs)
            else:
                #Mensaje de error detallado
                return jsonify({
                    "msg": "Acceso denegado. Rol insuficiente.", 
                    "role_required": roles
                }), 403
        return decorator
    return wrapper

# decoradores especificos

def admin_required(fn):
    """Solo permite el acceso a usuarios con rol 'admin'."""
    return roles_required("admin")(fn)

def mod_required(fn):
    """Solo permite el acceso a usuarios con rol 'admin' o 'mod'."""
    return roles_required("admin", "mod")(fn)

# Puedes agregar más si es necesario:
# def user_required(fn):
#     """Permite el paso a cualquier usuario autenticado (admin, mod, user)."""
#     return roles_required("admin", "mod", "user")(fn)