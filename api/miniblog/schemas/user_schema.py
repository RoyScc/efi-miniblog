from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Usuario     
from ..extensions import ma      

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        load_instance = True
        fields = ('id', 'nombre', 'correo', 'role', 'is_active')

user_schema = UserSchema()
users_schema = UserSchema(many=True)