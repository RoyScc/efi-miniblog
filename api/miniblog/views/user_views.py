from flask import Blueprint, jsonify, request
from ..models import db, Usuario
from ..schemas import user_schema, users_schema
from ..decorators.auth import roles_required 

user_bp = Blueprint('user_views', __name__, url_prefix='/api')

@user_bp.route('/users', methods=['GET'])
@roles_required(roles=['admin'])
def get_all_users():
    try:
        users = Usuario.query.all()
        return jsonify(users_schema.dump(users)), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener usuarios", "detalle": str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET', 'PATCH', 'DELETE'])
@roles_required(roles=['admin'])
def handle_user(user_id):
    user = Usuario.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if request.method == 'GET':
        return jsonify(user_schema.dump(user)), 200

    elif request.method == 'PATCH':
        data = request.get_json()
        if 'role' in data: user.role = data['role']
        if 'is_active' in data: user.is_active = data['is_active']
        try:
            db.session.commit()
            return jsonify({"mensaje": "Usuario actualizado", "user": user_schema.dump(user)}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al actualizar usuario", "detalle": str(e)}), 500

    elif request.method == 'DELETE':
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"mensaje": f"Usuario con id {user_id} eliminado"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al eliminar usuario", "detalle": str(e)}), 500