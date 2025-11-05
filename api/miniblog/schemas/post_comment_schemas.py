from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import Post, Comentario

ma = Marshmallow()

class PostSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        load_instance = True
        include_fk = True         #autor_id y categoria_id
        include_relationships = True  #autor y categoria

class CommentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Comentario
        load_instance = True
        include_fk = True         #autor_id y post_id
        include_relationships = True  #'autor' y 'post'

#endpoints
post_schema = PostSchema()
posts_schema = PostSchema(many=True)

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
