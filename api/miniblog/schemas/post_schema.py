from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..extensions import ma
from ..models.post import Post  

class PostSchema(SQLAlchemyAutoSchema):
    autor_nombre = fields.String(attribute="autor.nombre")
    fecha_creacion = fields.Method("format_fecha")
    class Meta:
        model = Post
        load_instance = True
        include_fk = True
        include_relationships = True

    def format_fecha(self, obj):
        return obj.fecha_creacion.strftime("%d/%m/%Y %H:%M")

post_schema = PostSchema()
posts_schema = PostSchema(many=True)