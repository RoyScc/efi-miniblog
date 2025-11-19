from ..extensions import ma
from ..models.categoria import Categoria

class CategoriaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Categoria
        load_instance = True
        fields = ('id', 'nombre') 

categoria_schema = CategoriaSchema()
categorias_schema = CategoriaSchema(many=True)