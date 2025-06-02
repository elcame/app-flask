from flask import Flask
from extensions import db
import json
import os
from datetime import datetime
from models.usuario import Usuario
from models.empresa import Empresa
from models.tractocamion import Tractocamion
from models.tipo_trabajador import TipoTrabajador
from models.trabajadores import Trabajadores
from models.manifiesto import Manifiesto

app = Flask(__name__)

# Configuración local
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sa:came@DESKTOP-JQSP6UN\\MYSQL/EMPRESAACR?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError(f"Object of type {type(x)} is not JSON serializable")

def export_table(model_class, filename):
    with app.app_context():
        data = []
        for item in model_class.query.all():
            item_dict = {}
            for column in model_class.__table__.columns:
                item_dict[column.name] = getattr(item, column.name)
            data.append(item_dict)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=datetime_handler)
        print(f"Exportados {len(data)} registros a {filename}")

if __name__ == '__main__':
    # Crear directorio para los datos si no existe
    os.makedirs('exported_data', exist_ok=True)
    
    # Exportar cada tabla
    export_table(Usuario, 'exported_data/usuarios.json')
    export_table(Empresa, 'exported_data/empresas.json')
    export_table(Tractocamion, 'exported_data/tractocamiones.json')
    export_table(TipoTrabajador, 'exported_data/tipos_trabajador.json')
    export_table(Trabajadores, 'exported_data/trabajadores.json')
    export_table(Manifiesto, 'exported_data/manifiestos.json')
    
    print("Exportación completada") 