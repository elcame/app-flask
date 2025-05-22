from flask import Flask, redirect, url_for, session, flash, get_flashed_messages , render_template
from extensions import db
from flask_login import LoginManager
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuración básica
    if os.environ.get('PYTHONANYWHERE_DOMAIN'):
        # Configuración para PythonAnywhere
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://GMDSOLUTIONS:abelardocamelo@GMDSOLUTIONS.mysql.pythonanywhere-services.com/GMDSOLUTIONS$ACR'
    else:
        # Configuración local
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sa:came@DESKTOP-JQSP6UN\\MYSQL/EMPRESAACR?driver=ODBC+Driver+17+for+SQL+Server'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = '2d288172ecd5b61ac97539ebbb927bee06d9584fc7a3e813c727429811246e56'
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # Asegurarse de que el directorio de uploads existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Configuración de Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'usuario_bp.login_form'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Inicialización de extensiones
    db.init_app(app)
    
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
            return Usuario.query.get(int(user_id))
    
    @app.route('/')
    def home():
        if 'user_id' not in session:
            return redirect(url_for('usuario_bp.login_form'))
        return redirect(url_for('manifiesto_bp.index'))
    
    @app.context_processor
    def utility_processor():
        return {
            'now': datetime.utcnow(),
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
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
