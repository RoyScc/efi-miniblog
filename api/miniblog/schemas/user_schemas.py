from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Usuario      # <-- 1. Importa 'Usuario' (el paquete)
from ..extensions import ma       # <-- 2. Importa 'ma' (de extensions)

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        load_instance = True
        fields = ('id', 'nombre', 'correo', 'role', 'is_active')

user_schema = UserSchema()
users_schema = UserSchema(many=True)