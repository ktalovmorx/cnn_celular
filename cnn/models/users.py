# -*- coding: UTF-8 -*-
#!/usr/bin/env python 

from .commons import db


class User(db.Model):
    '''
    Datos de usuarios
    '''
    
    __tablename__ = 'recommender_users'

    id = db.Column(db.Integer, primary_key=True, comment="Identificador único de la oferta")
    username = db.Column(db.String(80), nullable=True, comment="Nombre de usuario")
    userlastname = db.Column(db.String(80), nullable=True, comment="Apellido del usuario")
    usermail = db.Column(db.String(120), unique=True, nullable=False, comment="Correo electrónico del usuario")
    password_hash = db.Column(db.String(128), nullable=False, comment="Contraseña del usuario")

    def __repr__(self):
        return f'<User {self.usermail}>'