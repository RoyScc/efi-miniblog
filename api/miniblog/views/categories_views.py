from flask import Blueprint, request, jsonify
from ..models import db
from ..models.categoria import Categoria 
from ..schemas.categoria_schema import categoria_schema, categorias_schema 
from flask_jwt_extended import jwt_required

from ..decorators.auth import admin_required, mod_required

categories_bp = Blueprint('categories_api', __name__, url_prefix='/api/categories')


@categories_bp.route('/', methods=['GET'])
@jwt_required()
def get_categories():
    all_categories = Categoria.query.order_by(Categoria.nombre).all()
    result = categorias_schema.dump(all_categories)
    return jsonify(result)

@categories_bp.route('/', methods=['POST'])
@mod_required
def create_category():
    data = request.get_json()
    
    if 'nombre' not in data:
        return jsonify({"msg": "El campo 'nombre' es obligatorio."}), 400
    
    if Categoria.query.filter_by(nombre=data['nombre']).first():
        return jsonify({"msg": "Esa categoría ya existe."}), 400

    try:
        nueva_categoria = categoria_schema.load(data)
        db.session.add(nueva_categoria)
        db.session.commit()
        return categoria_schema.dump(nueva_categoria), 201 
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al crear la categoría.", "error": str(e)}), 500

@categories_bp.route('/<int:id>', methods=['PUT'])
@mod_required
def update_category(id):
    categoria = Categoria.query.get_or_404(id) 
    data = request.get_json()

    if 'nombre' not in data:
        return jsonify({"msg": "El campo 'nombre' es obligatorio."}), 400

    existing_cat = Categoria.query.filter_by(nombre=data['nombre']).first()
    if existing_cat and existing_cat.id != id:
        return jsonify({"msg": "Ese nombre de categoría ya está en uso."}), 400
    
    # Actualiza el nombre
    categoria.nombre = data['nombre']
    
    try:
        db.session.commit()
        return categoria_schema.dump(categoria) 
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al actualizar la categoría.", "error": str(e)}), 500

@categories_bp.route('/<int:id>', methods=['DELETE'])
@admin_required 
def delete_category(id):
    categoria = Categoria.query.get_or_404(id)
   
    if categoria.posts:
        return jsonify({"msg": "No se puede borrar la categoría porque tiene posts asociados."}), 400
        
        
    try:
        db.session.delete(categoria)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al borrar la categoría.", "error": str(e)}), 500