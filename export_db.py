from app import create_app, db
from models.usuario import Usuario
from models.empresa import Empresa
from models.tractocamion import Tractocamion
from models.tipo_trabajador import TipoTrabajador
from models.trabajadores import Trabajadores
from models.manifiesto import Manifiesto
import json
from datetime import datetime

def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError(f"Object of type {type(x)} is not JSON serializable")

def export_data():
    app = create_app()
    with app.app_context():
        # Exportar datos de cada modelo
        data = {
            'usuarios': [user.to_dict() for user in Usuario.query.all()],
            'empresas': [emp.to_dict() for emp in Empresa.query.all()],
            'tractocamiones': [trac.to_dict() for trac in Tractocamion.query.all()],
            'tipos_trabajador': [tipo.to_dict() for tipo in TipoTrabajador.query.all()],
            'trabajadores': [trab.to_dict() for trab in Trabajadores.query.all()],
            'manifiestos': [man.to_dict() for man in Manifiesto.query.all()]
        }
        
        # Guardar en archivo JSON
        with open('db_export.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=datetime_handler)
        
        print("Datos exportados exitosamente a db_export.json")

if __name__ == '__main__':
    export_data() 