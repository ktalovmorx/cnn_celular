from enum import Enum
from .commons import db, UserMixin
from sqlalchemy.orm import relationship

# Definir el Enum para los roles
class RoleEnum(Enum):
    paciente = 'paciente'
    doctor = 'doctor'
    admin = 'admin'

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
    address = db.Column(db.String(256), nullable=True, default="-", comment="Direccion")

    def __repr__(self):
        return f'<User {self.usermail}, Role: {self.role}>'

class Citologia(db.Model):
    '''
    Imagenes de las células
    '''
    __tablename__ = 'citologias'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Relación con User
    fecha = db.Column(db.Date, nullable=False)
    imagenes = db.Column(db.LargeBinary, nullable=True)  # Almacenar todas las imágenes como un solo arreglo binario
    diagnostico = db.Column(db.String(255), nullable=True)
    laboratorio = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', backref=db.backref('citologias', lazy=True))

    def __repr__(self):
        return f'<Citologia {self.id}, User: {self.user.username}, Fecha: {self.fecha}>'