from app import create_app, db
from models.usuario import Usuario
from models.empresa import Empresa
from models.tractocamion import Tractocamion
from models.tipo_trabajador import TipoTrabajador
from models.trabajadores import Trabajadores
from models.manifiesto import Manifiesto
import json
from datetime import datetime

def import_data():
    app = create_app()
    with app.app_context():
        # Crear todas las tablas
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
        
        print("Datos importados exitosamente")

if __name__ == '__main__':
    import_data() 