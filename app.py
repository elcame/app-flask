from flask import Flask, redirect, url_for, session, flash, get_flashed_messages , render_template, jsonify, send_file
from extensions import db
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user, current_user
from datetime import datetime, UTC
import os
from dotenv import load_dotenv
import json
from flask_migrate import Migrate
import logging

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Verificar variables de entorno
logger.info("Verificando variables de entorno:")
logger.info(f"GITHUB_REPO_URL: {os.environ.get('GITHUB_REPO_URL')}")
logger.info(f"GITHUB_TOKEN: {'Configurado' if os.environ.get('GITHUB_TOKEN') else 'No configurado'}")

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración básica
if os.environ.get('RENDER'):
    # Configuración para Render
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    # En Render, usamos GitHub Storage para persistencia
    app.config['UPLOAD_FOLDER'] = '/opt/render/project/src/uploads'
    
    # Verificar si existe el directorio persistente
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        logger.info(f"Creando directorio persistente: {app.config['UPLOAD_FOLDER']}")
        try:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            # Crear un archivo de prueba para verificar permisos
            test_file = os.path.join(app.config['UPLOAD_FOLDER'], 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            logger.info("Directorio persistente creado y verificado correctamente")
        except Exception as e:
            logger.error(f"Error al crear directorio persistente: {str(e)}")
            # Intentar usar un directorio alternativo
            app.config['UPLOAD_FOLDER'] = '/opt/render/project/src/tmp_uploads'
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            logger.info(f"Usando directorio alternativo: {app.config['UPLOAD_FOLDER']}")
    
    # Crear subcarpeta para la empresa 1
    empresa_folder = os.path.join(app.config['UPLOAD_FOLDER'], '1')
    os.makedirs(empresa_folder, exist_ok=True)
    
    # Crear carpeta para la fecha actual
    fecha_actual = datetime.now().strftime('%d-%m-%Y')
    carpeta_fecha = os.path.join(empresa_folder, fecha_actual)
    os.makedirs(carpeta_fecha, exist_ok=True)
    
    logger.info(f"Configuración de carpetas en Render:")
    logger.info(f"- Carpeta base: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"- Carpeta empresa: {empresa_folder}")
    logger.info(f"- Carpeta fecha actual: {carpeta_fecha}")
    
    # Verificar permisos de las carpetas
    try:
        test_file = os.path.join(carpeta_fecha, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        logger.info("Permisos de escritura verificados correctamente")
    except Exception as e:
        logger.error(f"Error al verificar permisos: {str(e)}")
elif os.environ.get('PYTHONANYWHERE_DOMAIN'):
    # Configuración para PythonAnywhere
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://GMDSOLUTIONS:abelardocamelo@GMDSOLUTIONS.mysql.pythonanywhere-services.com/GMDSOLUTIONS$ACR'
    app.config['UPLOAD_FOLDER'] = 'uploads'
else:
    # Configuración local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://acr_db_user:8QBqTTLlIDOD4ROq1vLWxfRCDzBtvOPB@dpg-d0nld0qli9vc73a1ng9g-a.oregon-postgres.render.com/acr_db'
    app.config['UPLOAD_FOLDER'] = 'uploads'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Crear carpetas necesarias
logger.info(f"Creando carpetas en: {app.config['UPLOAD_FOLDER']}")
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
logger.info(f"Carpeta uploads creada en: {app.config['UPLOAD_FOLDER']}")

# Crear subcarpeta para la empresa 1
empresa_folder = os.path.join(app.config['UPLOAD_FOLDER'], '1')
os.makedirs(empresa_folder, exist_ok=True)
logger.info(f"Subcarpeta empresa creada en: {empresa_folder}")

# Crear carpetas para Excel
os.makedirs('excel', exist_ok=True)
os.makedirs('excel/manifiestos', exist_ok=True)
os.makedirs('excel/reportes', exist_ok=True)
logger.info("Carpetas de Excel creadas")

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'usuario_bp.login_form'
login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Inicialización de extensiones
db.init_app(app)
migrate = Migrate(app, db)

# Intentar inicializar GitHub Storage
try:
    from extensions.github_storage import github_storage
    if github_storage is None or not github_storage.initialized:
        logger.warning("GitHub Storage no está disponible. Se usará almacenamiento local.")
        # Configurar almacenamiento local
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        logger.info(f"Configurado almacenamiento local en: {app.config['UPLOAD_FOLDER']}")
    else:
        logger.info("GitHub Storage inicializado correctamente")
        # Crear estructura de carpetas en GitHub
        try:
            # Crear estructura de carpetas local primero
            local_upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
            os.makedirs(local_upload_folder, exist_ok=True)
            empresa_folder = os.path.join(local_upload_folder, '1')
            os.makedirs(empresa_folder, exist_ok=True)
            
            # Intentar crear estructura en GitHub
            if github_storage.save_file(file=None, path='uploads/1/.gitkeep'):
                logger.info("Estructura de carpetas creada en GitHub")
            else:
                logger.warning("No se pudo crear la estructura en GitHub. Usando solo almacenamiento local.")
        except Exception as e:
            logger.error(f"Error al crear estructura en GitHub: {str(e)}")
            # Fallback a almacenamiento local
            app.config['UPLOAD_FOLDER'] = local_upload_folder
            logger.info(f"Fallback a almacenamiento local en: {app.config['UPLOAD_FOLDER']}")
except Exception as e:
    logger.error(f"Error al inicializar GitHub Storage: {str(e)}")
    github_storage = None
    # Configurar almacenamiento local
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    logger.info(f"Configurado almacenamiento local en: {app.config['UPLOAD_FOLDER']}")

# Asegurar que las carpetas necesarias existan
try:
    # Crear carpeta base de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Crear subcarpeta para la empresa 1
    empresa_folder = os.path.join(app.config['UPLOAD_FOLDER'], '1')
    os.makedirs(empresa_folder, exist_ok=True)
    
    logger.info(f"Estructura de carpetas local configurada:")
    logger.info(f"- Carpeta base: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"- Carpeta empresa: {empresa_folder}")
except Exception as e:
    logger.error(f"Error al crear estructura de carpetas local: {str(e)}")

# Registro de blueprints
with app.app_context():
    # Importar modelos
    from models.usuario import Usuario
    from models.empresa import Empresa
    from models.tractocamion import Tractocamion
    from models.tipo_trabajador import TipoTrabajador
    from models.trabajadores import Trabajadores
    from models.manifiesto import Manifiesto

    # Importar blueprints
    from routes.usuario_routes import usuario_bp
    from routes.empresa_routes import empresa_bp
    from routes.tractocamion_routes import tractocamion_bp
    from routes.trabajadores_routes import trabajadores_bp
    from routes.manifiesto_routes import manifiesto_bp
    from routes.procesar_pdfs_routes import procesar_pdfs_bp
    from routes.pagos_routes import pagos_bp
    from routes.tanqueo_routes import tanqueo_bp
    from routes.mantenimiento_routes import mantenimiento_bp
    from routes.seguro_routes import seguro_bp
    from routes.auth_routes import auth_bp
    from routes.manifiestos_routes import manifiestos_bp
    from routes.exportar_routes import exportar_bp

    # Registrar blueprints
    app.register_blueprint(usuario_bp)
    app.register_blueprint(empresa_bp)
    app.register_blueprint(tractocamion_bp)
    app.register_blueprint(trabajadores_bp)
    app.register_blueprint(manifiesto_bp)
    app.register_blueprint(procesar_pdfs_bp, url_prefix='/procesar_pdfs')
    app.register_blueprint(pagos_bp)
    app.register_blueprint(tanqueo_bp)
    app.register_blueprint(mantenimiento_bp)
    app.register_blueprint(seguro_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(manifiestos_bp)
    app.register_blueprint(exportar_bp)

    # Configurar el user_loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('usuario_bp.login_form'))
    return redirect(url_for('usuario_bp.manifiestos'))

@app.context_processor
def inject_now():
    return {
        'now': datetime.now(UTC),
        'get_flashed_messages': get_flashed_messages
    }

# Manejo de errores
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/import-data', methods=['GET', 'POST'])
def import_data():
    try:
        with app.app_context():
            # Eliminar todas las tablas existentes
            db.drop_all()
            
            # Crear todas las tablas sin restricciones
            db.create_all()
            
            # Cargar datos del archivo JSON
            with open('db_export.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Importar datos en orden para respetar las relaciones
            # 1. Tipos de trabajador
            for tipo_data in data['tipos_trabajador']:
                tipo = TipoTrabajador(**tipo_data)
                db.session.add(tipo)
            db.session.commit()
            
            # 2. Empresas
            for emp_data in data['empresas']:
                emp = Empresa(**emp_data)
                db.session.add(emp)
            db.session.commit()
            
            # 3. Tractocamiones
            for trac_data in data['tractocamiones']:
                trac = Tractocamion(**trac_data)
                db.session.add(trac)
            db.session.commit()
            
            # 4. Trabajadores
            for trab_data in data['trabajadores']:
                trab = Trabajadores(**trab_data)
                db.session.add(trab)
            db.session.commit()
            
            # 5. Usuarios
            for user_data in data['usuarios']:
                user = Usuario(**user_data)
                db.session.add(user)
            db.session.commit()
            
            # 6. Manifiestos
            for man_data in data['manifiestos']:
                man = Manifiesto(**man_data)
                db.session.add(man)
            db.session.commit()
            
            return jsonify({'message': 'Datos importados exitosamente'}), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Configuración para desarrollo local
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
