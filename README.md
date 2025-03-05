
<h3>Crear entorno virtual</h3>

```
    >>> cd cnn_project
    >>> python -m venv virtual
```

<h3>Activar entorno virtual</h3>

```
    >>> cd cnn_project
    >>> virtual\Scripts\activate
```

<h3>Instalar dependencias</h3>

```
    >>> python.exe -m pip install --upgrade pip
    >>> pip install -r requirements.txt
```

<h3>Crear la base de datos</h3>

```
    >>> psql
    >>> CREATE USER tao WITH PASSWORD 'root';
    >>> ALTER USER tao CREATEDB;
    >>> ALTER USER tao WITH SUPERUSER;
    >>> CREATE DATABASE recommender_system WITH OWNER = tao;
    >>> GRANT ALL PRIVILEGES ON DATABASE recommender_system TO tao;
    >>> COMMENT ON DATABASE recommender_system IS 'Base de datos de recomendacion';
```

<h3>Inicializar la base de datos</h3>

```
>>> cd /D D:\SOFTNOW\PROYECTOS\cnn_project
>>> flask db init
>>> flask db migrate -m "Initial migration"
>>> flask db upgrade
```

<h3>Para agregar una nueva tabla</h3>

```
>>> cd /D D:\SOFTNOW\PROYECTOS\cnn_project
>>> flask db migrate -m "Comentario del cambio"
>>> flask db upgrade
```

<h3>Reiniciar datos (opcional)</h3>

```
# Borrar la carpeta /migrations
>>> cd /D D:\SOFTNOW\PROYECTOS\cnn_project
>>> flask shell
>>> from recommender.models.commons import db
>>> db.drop_all()
```