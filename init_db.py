from app import create_app, db
from models.usuario import Usuario
from models.empresa import Empresa
from models.tractocamion import Tractocamion
from models.tipo_trabajador import TipoTrabajador
from models.trabajadores import Trabajadores
from models.manifiesto import Manifiesto
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def init_database():
    print("Iniciando la base de datos...")
    app = create_app()
    
    # Verificar la configuración de la base de datos
    print("\nConfiguración de la base de datos:")
    print(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    with app.app_context():
        try:
            print("\nCreando tablas...")
            db.create_all()
            print("Tablas creadas exitosamente")
            
            # Verificar si hay datos
            print("\nVerificando datos en las tablas:")
            print(f"Usuarios: {Usuario.query.count()}")
            print(f"Empresas: {Empresa.query.count()}")
            print(f"Tractocamiones: {Tractocamion.query.count()}")
            print(f"Tipos de trabajador: {TipoTrabajador.query.count()}")
            print(f"Trabajadores: {Trabajadores.query.count()}")
            print(f"Manifiestos: {Manifiesto.query.count()}")
            
            # Verificar la conexión
            db.session.execute('SELECT 1')
            print("\nConexión a la base de datos exitosa")
            
        except Exception as e:
            print(f"\nError durante la inicialización: {str(e)}")
            raise

if __name__ == '__main__':
    init_database() 