# -*- coding: UTF-8 -*-
#!/usr/bin/env python 

from .commons import db


class Profile(db.Model):
    '''
    Datos de perfiles
    '''
    
    __tablename__ = 'recommender_user_profiles'

    id = db.Column(db.Integer, primary_key=True, comment="Identificador único del perfil")
    alias = db.Column(db.String(80), unique=True, nullable=False, comment="Alias único del usuario")
    email = db.Column(db.String(120), unique=True, nullable=False, comment="Correo electrónico único del perfil")
    name = db.Column(db.String(100), nullable=False, comment="Nombre de la persona a la que pertenece el perfil")
    description = db.Column(db.Text, nullable=True, comment="Breve descripción del perfil")
    links = db.Column(db.String(255), nullable=True, comment="Enlaces a redes sociales o portafolio (ejemplo: LinkedIn, GitHub)")
    awards = db.Column(db.Text, nullable=True, comment="Premios o competiciones en los que ha participado el perfil")
    languages = db.Column(db.Text, nullable=True, comment="Idiomas y nivel que posee el perfil (ejemplo: Inglés - Avanzado)")
    certifications = db.Column(db.Text, nullable=True, comment="Certificados obtenidos por el perfil")
    experience_time = db.Column(db.Date, nullable=True, comment="Fecha de inicio de la experiencia laboral hasta la fecha")
    keywords = db.Column(db.Text, nullable=True, comment="Palabras clave que identifican el perfil")
    company_jobs = db.Column(db.Text, nullable=True, comment="Empresas en las que ha trabajado (lista separada por comas)")
    jobs_date = db.Column(db.Text, nullable=True, comment="Fechas de trabajos (puede guardarse como JSON o texto) Ejemplo: ['2021-01-01', '2023-01-01']")
    education = db.Column(db.Text, nullable=True, comment="Centros de estudios donde se ha formado el perfil")
    jobs_duration = db.Column(db.Text, nullable=True, comment="Duración de los distintos trabajos (puede usarse JSON o texto) Ejemplo: [{'job': 'Dev', 'duration': '2 years'}]")

    def __repr__(self):
        return f'<Profile {self.name}>'