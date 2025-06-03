from flask import Flask, redirect, url_for, session, flash, get_flashed_messages , render_template, jsonify
from extensions import db
from flask_login import LoginManager, login_required
from datetime import datetime, UTC
import os
# from dotenv import load_dotenv
import json
from flask_migrate import Migrate

# Cargar variables de entorno
# load_dotenv()

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración básica
if os.environ.get('RENDER'):
    # Configuración para Render
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    # En Render, usamos una carpeta persistente para los uploads
    app.config['UPLOAD_FOLDER'] = '/opt/render/project/src/uploads'
    # Asegurarse de que la carpeta de uploads existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Crear subcarpeta para la empresa 1
    empresa_folder = os.path.join(app.config['UPLOAD_FOLDER'], '1')
    os.makedirs(empresa_folder, exist_ok=True)
    print(f"Carpetas creadas en Render: {app.config['UPLOAD_FOLDER']} y {empresa_folder}")
    
    # Crear carpeta para la fecha actual si no existe
    fecha_actual = datetime.now().strftime('%d-%m-%Y')
    carpeta_fecha = os.path.join(empresa_folder, fecha_actual)
    os.makedirs(carpeta_fecha, exist_ok=True)
    print(f"Carpeta de fecha creada: {carpeta_fecha}")
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
print(f"Creando carpetas en: {app.config['UPLOAD_FOLDER']}")  # Debug log
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
print(f"Carpeta uploads creada en: {app.config['UPLOAD_FOLDER']}")  # Debug log

# Crear subcarpeta para la empresa 1
empresa_folder = os.path.join(app.config['UPLOAD_FOLDER'], '1')
os.makedirs(empresa_folder, exist_ok=True)
print(f"Subcarpeta empresa creada en: {empresa_folder}")  # Debug log

# Crear carpetas para Excel
os.makedirs('excel', exist_ok=True)
os.makedirs('excel/manifiestos', exist_ok=True)
os.makedirs('excel/reportes', exist_ok=True)
print("Carpetas de Excel creadas")  # Debug log

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'usuario_bp.login_form'
login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Inicialización de extensiones
db.init_app(app)
migrate = Migrate(app, db)

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

    # Registrar blueprints
    app.register_blueprint(usuario_bp)
    app.register_blueprint(empresa_bp)
    app.register_blueprint(tractocamion_bp)
    app.register_blueprint(trabajadores_bp)
    app.register_blueprint(manifiesto_bp)
    app.register_blueprint(procesar_pdfs_bp)
    app.register_blueprint(pagos_bp)
    app.register_blueprint(tanqueo_bp)
    app.register_blueprint(mantenimiento_bp)
    app.register_blueprint(seguro_bp)

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
