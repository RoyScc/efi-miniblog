from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..extensions import ma
from ..models.post import Post  

class PostSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        load_instance = True
        include_fk = True
        include_relationships = True

post_schema = PostSchema()
posts_schema = PostSchema(many=True)