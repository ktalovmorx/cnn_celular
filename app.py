from flask import Flask, request, jsonify, send_from_directory, json, url_for, redirect, flash, render_template
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import flask_bcrypt
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api
from flask_login import login_user
from werkzeug.utils import secure_filename
import os
from cnn.cnn_model import CNNModel
from cnn import create_app
from cnn.models import User, Citologia, ImagenCitologia
from dotenv import load_dotenv
from enum import Enum
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import logging
from PIL import Image
load_dotenv()

# -- Configuración del logger
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
)
_logger = logging.getLogger(__name__)

# -- Read .env file
try:
    PORT = int(os.getenv('flask_port'))
    MODEL_NAME = os.getenv('model_name')
    PREDICTOR_NAME = os.getenv('predictor_name')
except:
    raise ValueError("PORT variable is not defined")

# Crear la aplicación Flask
app, db = create_app()

login_manager = LoginManager(app)
login_manager.login_view = "login"  # -- Redirigir a la vista /login si no está autenticado

#Manejar contraseñas de forma segura
bcrypt = flask_bcrypt.Bcrypt(app)
CORS(app)
api = Api(app)

# -- Inicializa la base de datos
db.init_app(app)
migrate = Migrate(app, db)

# -- Extensiones permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm', 'tiff'}

class RoleEnum(Enum):
    paciente = 'paciente'
    doctor = 'doctor'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/show_image/<int:cid>/<int:uid>', methods=['GET'])
@login_required
def show_citology_images(cid: int, uid: int):
    '''
    Muestra las imágenes de la citología
    cid (int) -> Id de la citología
    uid (int) -> Id del usuario 
    '''
    try:
        # -- Obtener la citología por ID
        citologia = Citologia.query.filter_by(id=cid).first()

        # -- Obtener el paciente asociado
        pacient_user = User.query.get(uid) if uid else None

        if pacient_user is None:
            flash('No se ha encontrado el paciente indicado', 'error')
            return redirect(url_for('get_pacient_list'))
        
        # -- Si no se encuentra la citología, retornar error
        if not citologia:
            flash('Citología no encontrada', 'error')
            return redirect(url_for('get_pacient_list'))

        # -- Obtener todas las imágenes asociadas a la citología
        imagenes = ImagenCitologia.query.filter_by(citologia_id=cid).all()

        if not imagenes:
            flash('No se han encontrado imágenes para esta citología', 'error')
            return redirect(url_for('get_pacient_list'))
        
        # -- Pasar las imágenes completas al template
        return render_template('image_carousel.html', 
                               images=imagenes, 
                               user_role=current_user.role.value, 
                               pacient_user=pacient_user) 

    except Exception as e:
        flash(f'Error al mostrar las imágenes: {str(e)}', 'error')
        return redirect(url_for('get_pacient_page'))


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    '''
    Captura y almacena los datos de la citología con múltiples imágenes
    '''
    try:
        fecha = request.form.get('citologia-date')
        codigo = request.form.get('citologia-code')
        files = request.files.getlist('citologia-images')
        laboratorio = request.form.get('citologia-lab')
        pacient_id = request.form.get('pacient_id')

        if not fecha or not codigo or not files:
            flash('Todos los campos son obligatorios', 'error')
            return render_template('404.html', message="Todos los campos son obligatorios", user_role=current_user.role.value)

        # -- Crear el nombre de la carpeta
        code_name = codigo.replace('@', '_').replace('.', '_').upper() + '_' + str(fecha).replace('-', '_')
        pacient_folder = os.path.join(app.config['UPLOAD_PATH'], code_name)
        
        # -- Crear la carpeta si no existe
        os.makedirs(pacient_folder, exist_ok=True)

        # -- Crear el objeto Citologia sin imágenes aún
        new_citologia = Citologia(
            user_id=int(pacient_id),
            doctor_id=current_user.id,
            folder=pacient_folder,
            fecha=fecha,
            diagnostico='N/A',
            laboratorio=laboratorio
        )

        db.session.add(new_citologia)
        db.session.commit()  # Guardamos la citología antes de asociar imágenes

        # -- Guardar imágenes como registros en ImagenCitologia
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(pacient_folder, filename)
                real_path = f'uploads/{code_name}/{filename}'

                # -- Verificar si la imagen es TIFF y convertirla a PNG
                if filename.lower().endswith('.tiff'):
                    with Image.open(file) as img:
                        png_filename = filename.replace('.tiff', '.png')
                        png_filepath = os.path.join(pacient_folder, png_filename)
                        real_path = f'uploads/{code_name}/{png_filename}'
                        img.save(png_filepath, 'PNG')  # Guardar como PNG
                
                else:
                    file.save(filepath)

                # -- Guardar la imagen en la base de datos
                new_image = ImagenCitologia(
                    citologia_id=new_citologia.id,
                    image_path=real_path
                )
                db.session.add(new_image)

        db.session.commit()  # Confirmamos todas las imágenes en la BD

        flash('Citología guardada con éxito', 'success')
        return redirect(url_for('get_pacient_page', uid=pacient_id))

    except Exception as e:
        db.session.rollback()  # Revertir cambios en caso de error
        flash(f'Error al subir la citología: {str(e)}', 'error')
        return render_template('notification.html', message=f'Error al subir la citología: {str(e)}')

@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory(app.static_folder, filename)

# Ruta para el diagnóstico
@app.route('/pacient_diagnostic', methods=['POST', 'GET'])
@login_required             # -- Restringe el acceso a usuarios autenticados
def diagnosticar():

    if request.method == 'GET':
        return "<h1>En construcción...</h1>", 200
    
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

    # -- Cargar el modelo
    CNNModel.load_h5_model(model_path=f'./cnn/{MODEL_NAME}')
    predictor = CNNModel.get_predictor(predictor_path=f'./cnn/{PREDICTOR_NAME}')

    # -- Realizar la predicción
    try:
        cat_id = CNNModel.categorizador_local(file_path)
        return jsonify({'diagnostico': predictor[cat_id].upper()}), 200
    except Exception as e:
        return jsonify({'error': 'Ocurrió un error al procesar la imagen', 'details': str(e)}), 500

@app.route('/pacient_list', methods=['GET'])
@login_required             # -- Restringe el acceso a usuarios autenticados
def get_pacient_list():
    '''
    Obtiene la lista de pacientes
    '''
    # -- Obtener los usuarios que tienen rol 'paciente', ordenados por lastname
    pacientes = User.query.filter_by(role='paciente').order_by(User.lastname).all()

    return render_template('pacient_list.html', user=current_user, pacientes=pacientes)

@app.route('/pacient_page/<int:uid>', methods=['GET'])
@app.route('/pacient_page', methods=['GET'])
# -- Restringe el acceso a usuarios autenticados
@login_required
def get_pacient_page(uid=None):
    '''
    Retorna la pagina del paciente
    '''

    # Si se proporciona un `uid`, buscar el usuario en la base de datos
    pacient_user = User.query.get(uid) if uid else current_user

    # Si no existe el usuario con ese `uid`, redirigir con un mensaje de error
    if not pacient_user:
        flash('Usuario no encontrado', 'error')
        return render_template('notification.html', message='Usuario no encontrado')
    
    citologias = Citologia.query.filter_by(user_id=pacient_user.id).all()
    return render_template('pacient_page.html', doctor=current_user, user=pacient_user, user_role=current_user.role.value, citologias=citologias)

@app.route('/register', methods=['POST', 'GET'])
@login_required
def new_account():
    '''
    Registro de usuario
    '''
    if request.method == 'GET':
        return render_template('register.html'), 200

    try:
        # -- Intentar obtener los datos desde JSON o Form
        data = request.get_json() if request.is_json else request.form
        usermail = data.get('usermail', None)
        password = data.get('password', None)
        username = data.get('username', None) 
        lastname = data.get('lastname', None)
        role     = data.get('role', None)
        dni      = data.get('dni', None)
        address  = data.get('address', '-')
        phone_number = data.get('phone_number', '-')
        birthday = data.get('birthday', None)

        if None in (usermail,password,username, lastname, role):
            return render_template('register_failed.html', message='Registro fallido, intente de nuevo mas tarde ó contacte a un administrador'), 400

        # Convertir la fecha de nacimiento a un objeto datetime.date
        try:
            birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
        except ValueError:
            return render_template('register_failed.html', message='Fecha de nacimiento no válida'), 400
        
        # -- Verificar si el usuario ya existe
        existing_user = User.query.filter_by(usermail=usermail).first()
        if existing_user:
            return render_template('register_failed.html', message='Registro fallido, intente de nuevo mas tarde ó contacte a un administrador'), 400

        # -- Hashear la contraseña
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Guardar usuario en la base de datos
        new_user = User(usermail=usermail,
                        password_hash=hashed_password,
                        username=username,
                        lastname=lastname,
                        role=role,
                        dni=dni,
                        address=address,
                        phone_number=phone_number,
                        birthday=birthday
                        )
        db.session.add(new_user)
        db.session.commit()

        return render_template('user_registered.html', message='Usuario registrado satisfactoriamente'), 200

    except IntegrityError:
        db.session.rollback()
        return render_template('register_failed.html', message='Registro fallido, intente de nuevo mas tarde ó contacte a un administrador'), 400
    except Exception as e:
        return render_template('register_failed.html', message='Registro fallido, intente de nuevo mas tarde ó contacte a un administrador'), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Autenticación de usuario.
    - GET   : Indica que el método correcto es POST.
    - POST  : Procesa la autenticación.
    '''

    # -- Verificar si el usuario ya está autenticado
    if current_user.is_authenticated:
        if current_user.role.value == RoleEnum.paciente.value:
            return redirect(url_for('get_pacient_page'))
        elif current_user.role.value == RoleEnum.doctor.value:
            return redirect(url_for('get_pacient_list'))
        
    if request.method == 'GET':
        return render_template('login.html'), 200

    # -- Capturar los datos del formulario
    usermail = request.form.get('usermail')
    password = request.form.get('password')

    # Buscar al usuario en la base de datos
    user = User.query.filter_by(usermail=usermail).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        # -- Iniciar sesión con Flask-Login
        login_user(user)

        flash('Inicio de sesión exitoso', 'success')
        
        # -- Redirigir al usuario a la página que intentaba acceder
        next_page = request.args.get('next')

        if user.role.value == RoleEnum.paciente.value:
            return redirect(next_page or url_for('get_pacient_page'))
        elif user.role.value == RoleEnum.doctor.value:
            return redirect(next_page or url_for('get_pacient_list'))
        else:
            logout_user()
            return redirect(url_for('login'))
    else:
        flash('Correo electrónico o contraseña incorrectos', 'error')
        return redirect(url_for('login'))
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
def main():
    '''
    Pagina principal
    '''
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=PORT)
