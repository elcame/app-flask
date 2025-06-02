from flask import Flask
from extensions import db
import json
import os
import logging
from datetime import datetime
from models.usuario import Usuario
from models.empresa import Empresa
from models.tractocamion import Tractocamion
from models.tipo_trabajador import TipoTrabajador
from models.trabajadores import Trabajadores
from models.manifiesto import Manifiesto
# Cargar variables de entorno
# load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración para Render
DATABASE_URL = "postgresql://acr_db_user:8QBqTTLlIDOD4ROq1vLWxfRCDzBtvOPB@dpg-d0nld0qli9vc73a1ng9g-a.oregon-postgres.render.com/acr_db"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def test_db_connection():
    """Prueba la conexión a la base de datos"""
    try:
        with app.app_context():
            db.engine.connect()
            logger.info("Conexión a la base de datos exitosa")
            return True
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {str(e)}")
        return False

def import_data():
    """Importa datos desde db_export.json a la base de datos"""
    with app.app_context():
        try:
            # Verificar si el archivo existe
            if not os.path.exists('db_export.json'):
                logger.error("Archivo db_export.json no encontrado")
                return False

            # Leer datos del archivo JSON
            with open('db_export.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data:
                logger.warning("El archivo db_export.json está vacío")
                return False

            # Limpiar todas las tablas en orden inverso a las relaciones
            logger.info("Limpiando tablas existentes...")
            Manifiesto.query.delete()
            Usuario.query.delete()
            Trabajadores.query.delete()
            Tractocamion.query.delete()
            TipoTrabajador.query.delete()
            Empresa.query.delete()
            db.session.commit()
            logger.info("Tablas limpiadas exitosamente")

            # Importar datos en orden para respetar las relaciones
            # 1. Tipos de trabajador
            logger.info("Importando tipos de trabajador...")
            for tipo_data in data['tipos_trabajador']:
                tipo = TipoTrabajador(**tipo_data)
                db.session.add(tipo)
            db.session.commit()
            logger.info(f"Tipos de trabajador importados: {len(data['tipos_trabajador'])}")
            
            # 2. Empresas
            logger.info("Importando empresas...")
            for emp_data in data['empresas']:
                emp = Empresa(**emp_data)
                db.session.add(emp)
            db.session.commit()
            logger.info(f"Empresas importadas: {len(data['empresas'])}")
            
            # 3. Tractocamiones
            logger.info("Importando tractocamiones...")
            for trac_data in data['tractocamiones']:
                trac = Tractocamion(**trac_data)
                db.session.add(trac)
            db.session.commit()
            logger.info(f"Tractocamiones importados: {len(data['tractocamiones'])}")
            
            # 4. Trabajadores
            logger.info("Importando trabajadores...")
            for trab_data in data['trabajadores']:
                trab = Trabajadores(**trab_data)
                db.session.add(trab)
            db.session.commit()
            logger.info(f"Trabajadores importados: {len(data['trabajadores'])}")
            
            # 5. Usuarios
            logger.info("Importando usuarios...")
            for i, user_data in enumerate(data['usuarios']):
                # Si no es el primer usuario y tiene el mismo email, modificar el email
                if i > 0 and user_data['EMAIL'] == data['usuarios'][0]['EMAIL']:
                    user_data['EMAIL'] = f"admin{i+1}.{user_data['EMAIL']}"
                user = Usuario(**user_data)
                db.session.add(user)
            db.session.commit()
            logger.info(f"Usuarios importados: {len(data['usuarios'])}")
            
            # 6. Manifiestos
            logger.info("Importando manifiestos...")
            for man_data in data['manifiestos']:
                man = Manifiesto(**man_data)
                db.session.add(man)
            db.session.commit()
            logger.info(f"Manifiestos importados: {len(data['manifiestos'])}")
            
            logger.info("Importación completada exitosamente")
            return True

        except Exception as e:
            logger.error(f"Error al importar datos: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    try:
        # Probar conexión a la base de datos
        if not test_db_connection():
            raise Exception("No se pudo conectar a la base de datos")

        # Importar datos
        if import_data():
            logger.info("Proceso completado exitosamente")
        else:
            logger.error("La importación se completó con errores")
            
    except Exception as e:
        logger.error(f"Error general: {str(e)}") 