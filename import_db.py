from app import app, db
from models.usuario import Usuario
from models.empresa import Empresa
from models.tractocamion import Tractocamion
from models.tipo_trabajador import TipoTrabajador
from models.trabajadores import Trabajadores
from models.manifiesto import Manifiesto
import json
from datetime import datetime
import os

def import_data():
    # Configurar la conexión a PostgreSQL
    database_url = "postgresql://acr_db_user:8QBqTTLlIDOD4ROq1vLWxfRCDzBtvOPB@dpg-d0nld0qli9vc73a1ng9g-a.oregon-postgres.render.com/acr_db"
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    with app.app_context():
        print("Iniciando importación a PostgreSQL...")
        # Crear todas las tablas
        db.create_all()
        print("Tablas creadas exitosamente")
        
        # Cargar datos del archivo JSON
        with open('db_export.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Importar datos en orden para respetar las relaciones
        # 1. Tipos de trabajador
        print("\nImportando tipos de trabajador...")
        for tipo_data in data['tipos_trabajador']:
            tipo = TipoTrabajador(**tipo_data)
            db.session.add(tipo)
        db.session.commit()
        print(f"Tipos de trabajador importados: {len(data['tipos_trabajador'])}")
        
        # 2. Empresas
        print("\nImportando empresas...")
        for emp_data in data['empresas']:
            emp = Empresa(**emp_data)
            db.session.add(emp)
        db.session.commit()
        print(f"Empresas importadas: {len(data['empresas'])}")
        
        # 3. Tractocamiones
        print("\nImportando tractocamiones...")
        for trac_data in data['tractocamiones']:
            trac = Tractocamion(**trac_data)
            db.session.add(trac)
        db.session.commit()
        print(f"Tractocamiones importados: {len(data['tractocamiones'])}")
        
        # 4. Trabajadores
        print("\nImportando trabajadores...")
        for trab_data in data['trabajadores']:
            trab = Trabajadores(**trab_data)
            db.session.add(trab)
        db.session.commit()
        print(f"Trabajadores importados: {len(data['trabajadores'])}")
        
        # 5. Usuarios
        print("\nImportando usuarios...")
        for user_data in data['usuarios']:
            user = Usuario(**user_data)
            db.session.add(user)
        db.session.commit()
        print(f"Usuarios importados: {len(data['usuarios'])}")
        
        # 6. Manifiestos
        print("\nImportando manifiestos...")
        for man_data in data['manifiestos']:
            man = Manifiesto(**man_data)
            db.session.add(man)
        db.session.commit()
        print(f"Manifiestos importados: {len(data['manifiestos'])}")
        
        print("\nImportación completada exitosamente")

if __name__ == '__main__':
    import_data() 