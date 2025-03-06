from flask import Flask, request, jsonify, send_from_directory, json, url_for, redirect, flash, render_template
import flask_bcrypt
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Resource, Api
import os
from cnn.cnn_model import CNNModel
from cnn import create_app
from cnn.models import User
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
load_dotenv()

# -- Read .env file
try:
    PORT = int(os.getenv('flask_port'))
    MODEL_NAME = os.getenv('model_name')
except:
    raise ValueError("PORT variable is not defined")

# Crear la aplicación Flask
app, db = create_app()
app.secret_key = 'xxx123'

#Manejar contraseñas de forma segura
bcrypt = flask_bcrypt.Bcrypt(app)
CORS(app)
api = Api(app)

# -- Inicializa la base de datos
db.init_app(app)
migrate = Migrate(app, db)

# -- Extensiones permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    '''
    Permite la subida de un archivo al servidor
    '''

    file = request.files['file']
    if not file:
        return render_template('not_found.html', message='File not found')
    else:
        file.save(app.config['UPLOAD_PATH'] + '/' + file.filename)
        return render_template('not_found.html', message='File uploaded successfully')
    
@app.route('/', methods=['GET'])
def main():
    '''
    Pagina principal
    '''
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory(app.static_folder, filename)

# Ruta para el diagnóstico
@app.route('/pacient_diagnostic', methods=['POST'])
def diagnosticar():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No se envió ninguna imagen'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Formato de archivo no permitido'}), 400

    # Guardar la imagen en la carpeta estática
    file_path = os.path.join("static", file.filename)
    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({'error': 'No se pudo guardar la imagen', 'details': str(e)}), 500

    # Realizar la predicción
    predictor = CNNModel.get_predictor(MODEL_NAME)
    try:
        cat_id = CNNModel.categorizador_local(file_path)
        return jsonify({'diagnostico': predictor[cat_id].upper()}), 200
    except Exception as e:
        return jsonify({'error': 'Ocurrió un error al procesar la imagen', 'details': str(e)}), 500

@app.route('/pacient_list', methods=['POST'])
def get_pacient_list():
    '''
    '''
    return render_template('pacient_list.html')

@app.route('/register', methods=['POST', 'GET'])
def new_account():
    '''
    Registro de usuario
    '''
    if request.method == 'GET':
        return render_template('register.html'), 200

    try:
        # Intentar obtener los datos desde JSON o Form
        data = request.get_json() if request.is_json else request.form
        usermail = data.get('usermail', None)
        password = data.get('password', None)
        username = data.get('username', None) 
        lastname = data.get('lastname', None)

        if None in (usermail,password,username, lastname):
            return render_template('register_failed.html', message='Registro fallido, intente de nuevo mas tarde o contacte a un administrador')

        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(usermail=usermail).first()
        if existing_user:
            return jsonify({'message': 'El correo ya está registrado'}), 409

        # Hashear la contraseña
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Guardar usuario en la base de datos
        new_user = User(usermail=usermail, password_hash=hashed_password, username=username, lastname=lastname)
        db.session.add(new_user)
        db.session.commit()

        return render_template('user_registered.html', message='Usuario registrado satisfactoriamente')

    except IntegrityError:
        db.session.rollback()
        return render_template('register_failed.html', message='Registro fallido, intente de nuevo mas tarde o contacte a un administrador')
    except Exception as e:
        return render_template('register_failed.html', message='Registro fallido, intente de nuevo mas tarde o contacte a un administrador')

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Autenticación de usuario.
    - GET   : Indica que el método correcto es POST.
    - POST  : Procesa la autenticación.
    '''

    if request.method == 'GET':
        return render_template('login.html'), 200
    else:
        # -- Capturar los datos del formulario
        usermail = request.form.get('usermail')
        password = request.form.get('password')

        # Buscar al usuario en la base de datos
        user = User.query.filter_by(usermail=usermail).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('get_pacient_list'))
        else:
            flash('Correo electrónico o contraseña incorrectos', 'error')
            return redirect(url_for('login'))
    
if __name__ == '__main__':
    app.run(debug=True, port=PORT)
