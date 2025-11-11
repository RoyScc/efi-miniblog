from flask import Blueprint, request, jsonify
from ..models import db
from ..models.categoria import Categoria # Importa el modelo 
# Importa los schemas que acaba de crear
from ..schemas.categoria_schema import categoria_schema, categorias_schema 
from flask_jwt_extended import jwt_required

# Importa los decoradores de rol que creamos
from ..decorators.auth import admin_required, mod_required

# Crea un grupo de rutas
categories_bp = Blueprint('categories_api', __name__, url_prefix='/api/categories')

#ENDPOINTS
#listar todas Cualquiera con un token válido puede verlas.
@categories_bp.route('/', methods=['GET'])
@jwt_required()
def get_categories():
    all_categories = Categoria.query.order_by(Categoria.nombre).all()
    # Usa el schema 'many=True' para volcar la lista a JSON
    result = categorias_schema.dump(all_categories)
    return jsonify(result)

#POST: Crear categoría solo mod/admin"
@categories_bp.route('/', methods=['POST'])
@mod_required
def create_category():
    data = request.get_json()
    
    # Valida si el nombre viene
    if 'nombre' not in data:
        return jsonify({"msg": "El campo 'nombre' es obligatorio."}), 400
    
    # Valida si ya existe
    if Categoria.query.filter_by(nombre=data['nombre']).first():
        return jsonify({"msg": "Esa categoría ya existe."}), 400

    try:
        # Usa el schema para cargar y crear el objeto
        nueva_categoria = categoria_schema.load(data)
        db.session.add(nueva_categoria)
        db.session.commit()
        # objeto creado
        return categoria_schema.dump(nueva_categoria), 201 
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al crear la categoría.", "error": str(e)}), 500

#Actualizar categoría #
@categories_bp.route('/<int:id>', methods=['PUT'])
@mod_required # Solo mod y admin
def update_category(id):
    categoria = Categoria.query.get_or_404(id) # Si no la encuentra, da 404
    data = request.get_json()

    if 'nombre' not in data:
        return jsonify({"msg": "El campo 'nombre' es obligatorio."}), 400

    # Valida si el nuevo nombre ya existe (y no es la categoría misma)
    existing_cat = Categoria.query.filter_by(nombre=data['nombre']).first()
    if existing_cat and existing_cat.id != id:
        return jsonify({"msg": "Ese nombre de categoría ya está en uso."}), 400
    
    # Actualiza el nombre
    categoria.nombre = data['nombre']
    
    try:
        db.session.commit()
        return categoria_schema.dump(categoria) #objeto actualizado
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al actualizar la categoría.", "error": str(e)}), 500

#Borrar categoría #
# solo admin
@categories_bp.route('/<int:id>', methods=['DELETE'])
@admin_required #Solo 'admin' puede pasar.
def delete_category(id):
    categoria = Categoria.query.get_or_404(id)
    
    #la categoría tiene posts
    if categoria.posts:
        #No dejar borrar
        return jsonify({"msg": "No se puede borrar la categoría porque tiene posts asociados."}), 400
        #Poner los posts en General
        
    try:
        db.session.delete(categoria)
        db.session.commit()
        return '', 204 # 'No Content' - éxito en borrado
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al borrar la categoría.", "error": str(e)}), 500