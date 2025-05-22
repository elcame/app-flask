from app import create_app, db
from models.usuario import Usuario
from models.empresa import Empresa
from models.tractocamion import Tractocamion
from models.tipo_trabajador import TipoTrabajador
from models.trabajadores import Trabajadores
from models.manifiesto import Manifiesto
import json
from datetime import datetime, date
from decimal import Decimal
from flask import Flask

def datetime_handler(x):
    if isinstance(x, (datetime, date)):
        return x.isoformat()
    if isinstance(x, Decimal):
        return float(x)
    raise TypeError(f"Object of type {type(x)} is not JSON serializable")

def export_data():
    # Crear una nueva instancia de la aplicación sin cargar la configuración de app.py
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sa:came@DESKTOP-JQSP6UN\\MYSQL/EMPRESAACR?driver=ODBC+Driver+17+for+SQL+Server'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar la base de datos con la nueva configuración
    db.init_app(app)
    
    with app.app_context():
        print("Exportando datos de SQL Server local...")
        # Exportar datos de cada modelo
        data = {
            'usuarios': [user.as_dict() for user in Usuario.query.all()],
            'empresas': [emp.as_dict() for emp in Empresa.query.all()],
            'tractocamiones': [trac.as_dict() for trac in Tractocamion.query.all()],
            'tipos_trabajador': [tipo.as_dict() for tipo in TipoTrabajador.query.all()],
            'trabajadores': [trab.as_dict() for trab in Trabajadores.query.all()],
            'manifiestos': [man.as_dict() for man in Manifiesto.query.all()]
        }
        
        # Guardar en archivo JSON
        with open('db_export.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=datetime_handler)
        
        print("Datos exportados exitosamente a db_export.json")
        print(f"Usuarios exportados: {len(data['usuarios'])}")
        print(f"Empresas exportadas: {len(data['empresas'])}")
        print(f"Tractocamiones exportados: {len(data['tractocamiones'])}")
        print(f"Tipos de trabajador exportados: {len(data['tipos_trabajador'])}")
        print(f"Trabajadores exportados: {len(data['trabajadores'])}")
        print(f"Manifiestos exportados: {len(data['manifiestos'])}")

if __name__ == '__main__':
    export_data() 