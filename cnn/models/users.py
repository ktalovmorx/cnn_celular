from enum import Enum
from .commons import db, UserMixin

# Definir el Enum para los roles
class RoleEnum(Enum):
    paciente = 'paciente'
    doctor = 'doctor'

# -- Hereda UserMixin para compatibilidad con Flask-Login
class User(db.Model, UserMixin):
    '''
    Datos de usuarios
    '''
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, comment="Identificador único de la oferta")
    username = db.Column(db.String(80), nullable=True, comment="Nombre de usuario")
    lastname = db.Column(db.String(80), nullable=True, comment="Apellido del usuario")
    usermail = db.Column(db.String(120), unique=True, nullable=False, comment="Correo electrónico del usuario")
    phone_number = db.Column(db.String(24), nullable=True, comment="Teléfono")
    password_hash = db.Column(db.String(128), nullable=False, comment="Contraseña del usuario")
    role = db.Column(db.Enum(RoleEnum), nullable=False, default=RoleEnum.paciente, comment="Rol del usuario (paciente o doctor)")
    birthday = db.Column(db.Date, nullable=True, comment="Fecha de nacimiento")
    dni = db.Column(db.String(20), nullable=True, default="-", comment="DNI")
    address = db.Column(db.String(20), nullable=True, default="-", comment="Direccion")

    def __repr__(self):
        return f'<User {self.usermail}, Role: {self.role}>'
