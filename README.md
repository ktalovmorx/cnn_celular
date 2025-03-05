
############### Crear entorno virtual ############### 
>>> cd cnn_project
>>> python -m venv virtual

############### Activar entorno virtual ############### 
>>> cd cnn_project
>>> virtual\Scripts\activate

############### Instalar dependencias ############### 
>>> python.exe -m pip install --upgrade pip
>>> pip install -r requirements.txt

############### Crear la base de datos ############### 

CREATE USER tao WITH PASSWORD 'root';
ALTER USER tao CREATEDB;
ALTER USER tao WITH SUPERUSER;
CREATE DATABASE recommender_system WITH OWNER = tao;
GRANT ALL PRIVILEGES ON DATABASE recommender_system TO tao;
COMMENT ON DATABASE recommender_system IS 'Base de datos de recomendacion';

############### Inicializar la base de datos ############### 

>>> flask db init
>>> flask db migrate -m "Initial migration"
>>> flask db upgrade

############### Para agregar una nueva tabla ############### 

>>> flask db migrate -m "Comentario del cambio"
>>> flask db upgrade

############### Reiniciar datos (opcional) ############### 
# Borrar la carpeta /migrations
>>> flask shell
>>> from recommender.models.commons import db
>>> db.drop_all()