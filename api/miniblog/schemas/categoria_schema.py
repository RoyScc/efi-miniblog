from ..extensions import ma
from ..models.categoria import Categoria

class CategoriaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Categoria
        load_instance = True
        # No incluimos 'posts' aquí para no hacer la respuesta pesada
        fields = ('id', 'nombre') 

# Instancias (una para un objeto, otra para una lista)
categoria_schema = CategoriaSchema()
categorias_schema = CategoriaSchema(many=True)