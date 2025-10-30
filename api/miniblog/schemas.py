from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import Usuario

# Inicializacion    
ma = Marshmallow()

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        # 1. Le dice al esquema qué modelo "traducir"
        model = Usuario
        
        # 2. Le dice a Marshmallow que cree un objeto Usuario al cargar (útil para después)
        load_instance = True
        
        # 3. Define qué campos del modelo incluir (¡Checklist!)
        #    Usamos los nombres de tu models.py: 'nombre' y 'correo'
        fields = ('id', 'nombre', 'correo', 'role', 'is_active')

# Creamos instancias de los esquemas para usarlos
user_schema = UserSchema()            # Para manejar un solo usuario
users_schema = UserSchema(many=True)  # Para manejar listas de usuarios