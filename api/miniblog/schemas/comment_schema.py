from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..extensions import ma
from miniblog.models.comentario import Comentario


class CommentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Comentario
        load_instance = True
        include_fk = True          
        include_relationships = True 

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)