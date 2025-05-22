from app import create_app, db
from models.usuario import Usuario
from models.empresa import Empresa
from models.tractocamion import Tractocamion
from models.tipo_trabajador import TipoTrabajador
from models.trabajadores import Trabajadores
from models.manifiesto import Manifiesto

def init_database():
    print("Iniciando la base de datos...")
    app = create_app()
    with app.app_context():
        print("Creando tablas...")
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

if __name__ == '__main__':
    init_database() 