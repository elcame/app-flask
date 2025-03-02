from flask import Flask, redirect, url_for, session
from extensions import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sa:came@DESKTOP-JQSP6UN\\MYSQL/master?driver=ODBC+Driver+17+for+SQL+Server'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'

    db.init_app(app)

    with app.app_context():
        from models import Usuario, Empresa, Tractocamion, Pago, Tanqueo, Viajes, Mantenimiento, Conductor
        from routes import usuario_bp, empresa_bp, tractocamion_bp, pago_bp, tanqueo_bp, viajes_bp, mantenimiento_bp, conductor_bp

        app.register_blueprint(usuario_bp)
        app.register_blueprint(empresa_bp)
        app.register_blueprint(tractocamion_bp)
        app.register_blueprint(pago_bp)
        app.register_blueprint(tanqueo_bp)
        app.register_blueprint(viajes_bp)
        app.register_blueprint(mantenimiento_bp)
        app.register_blueprint(conductor_bp)

    @app.route('/')
    def home():
        return redirect(url_for('usuario_bp.login_form'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)