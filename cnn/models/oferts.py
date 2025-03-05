# -*- coding: UTF-8 -*-
#!/usr/bin/env python 

from .commons import db


class Ofert(db.Model):
    '''
    Datos de ofertas laborales
    '''
    
    __tablename__ = 'recommender_ofertas_laborales'

    id = db.Column(db.Integer, primary_key=True, comment="Identificador único de la oferta")
    username = db.Column(db.String(80), unique=True, nullable=False, comment="Nombre de usuario que creó la oferta")
    email = db.Column(db.String(120), unique=True, nullable=False, comment="Correo electrónico del creador de la oferta")
    category = db.Column(db.String(100), nullable=True, comment="Categoría de la empresa")
    source_page = db.Column(db.String(255), nullable=True, comment="Página de origen de la oferta")
    _hash = db.Column(db.String(255), unique=True, nullable=False, comment="Hash de la oferta")
    title = db.Column(db.String(200), nullable=False, comment="Título o encabezado de la oferta")
    organization = db.Column(db.String(200), nullable=True, comment="Empresa que oferta el puesto")
    url = db.Column(db.String(255), nullable=True, comment="URL de la página web donde se encuentra la oferta")
    logo = db.Column(db.String(255), nullable=True, comment="Logo de la empresa que oferta el puesto")
    location = db.Column(db.String(200), nullable=True, comment="Ubicación física de la empresa")
    requirements = db.Column(db.Text, nullable=True, comment="Requerimientos generales de la oferta")
    minimun = db.Column(db.String(50), nullable=True, comment="Mínimo de años de experiencia requeridos")
    languages = db.Column(db.Text, nullable=True, comment="Idiomas requeridos para el puesto")
    education = db.Column(db.String(100), nullable=True, comment="Nivel de educación requerido para el puesto")
    skills = db.Column(db.Text, nullable=True, comment="Habilidades necesarias para el puesto")
    begin_date = db.Column(db.Date, nullable=True, comment="Fecha de inicio del contrato")
    salary = db.Column(db.Integer, nullable=True, comment="Salario ofrecido para el puesto")
    work_position = db.Column(db.String(200), nullable=True, comment="Posición requerida en la empresa")
    workday = db.Column(db.String(100), nullable=True, comment="Jornada laboral (completa, parcial, etc.)")
    description = db.Column(db.Text, nullable=True, comment="Breve descripción de la oferta")
    keywords = db.Column(db.Text, nullable=True, comment="Palabras clave que describen la oferta")
    others = db.Column(db.Text, nullable=True, comment="Otros datos de interés como el número de vacantes y de inscritos")

    def __repr__(self):
        return f'<Ofert {self.title}>'