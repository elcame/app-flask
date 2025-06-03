import os
import logging
import tempfile
import shutil
from git import Repo, GitCommandError
from datetime import datetime

logger = logging.getLogger(__name__)

class GitHubStorage:
    def __init__(self):
        self.repo_url = os.environ.get('GITHUB_REPO_URL')
        self.token = os.environ.get('GITHUB_TOKEN')
        self.temp_dir = None
        self.repo = None
        self.initialized = False
        
        if not self.repo_url or not self.token:
            logger.warning("GitHub Storage no disponible: Variables de entorno GITHUB_REPO_URL o GITHUB_TOKEN no configuradas")
            return
            
        try:
            # Crear directorio temporal
            self.temp_dir = tempfile.mkdtemp()
            logger.info(f"Directorio temporal creado: {self.temp_dir}")
            
            # Construir URL con token
            repo_url_with_token = self.repo_url.replace('https://', f'https://{self.token}@')
            
            # Clonar repositorio
            try:
                self.repo = Repo.clone_from(repo_url_with_token, self.temp_dir)
                logger.info("Repositorio clonado exitosamente")
            except GitCommandError as e:
                logger.error(f"Error al clonar repositorio: {str(e)}")
                self._cleanup()
                return
                
            # Configurar git
            try:
                with self.repo.git.custom_environment(GIT_ASKPASS='echo'):
                    self.repo.config_writer().set_value("user", "name", "ACR Bot").release()
                    self.repo.config_writer().set_value("user", "email", "acr@example.com").release()
                logger.info("Configuración de git completada")
            except Exception as e:
                logger.error(f"Error al configurar git: {str(e)}")
                self._cleanup()
                return
                
            # Crear estructura de carpetas necesaria
            try:
                uploads_dir = os.path.join(self.temp_dir, 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                logger.info(f"Directorio uploads creado: {uploads_dir}")
                
                # Crear archivo .gitkeep para mantener la estructura
                gitkeep_path = os.path.join(uploads_dir, '.gitkeep')
                with open(gitkeep_path, 'w') as f:
                    f.write('')
                
                # Añadir y hacer commit de la estructura
                self.repo.index.add(['uploads/.gitkeep'])
                self.repo.index.commit("Crear estructura de carpetas")
                
                # Push al repositorio
                origin = self.repo.remote(name='origin')
                origin.push()
                logger.info("Estructura de carpetas creada en GitHub")
            except Exception as e:
                logger.error(f"Error al crear estructura de carpetas: {str(e)}")
                self._cleanup()
                return
                
            self.initialized = True
            logger.info("GitHub Storage inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error al inicializar GitHub Storage: {str(e)}")
            self._cleanup()
            
    def _cleanup(self):
        """Limpia los recursos temporales"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Directorio temporal eliminado: {self.temp_dir}")
            except Exception as e:
                logger.error(f"Error al eliminar directorio temporal: {str(e)}")
        self.temp_dir = None
        self.repo = None
        self.initialized = False
        
    def _check_initialization(self):
        """Verifica si el repositorio está inicializado correctamente"""
        if not self.initialized:
            logger.warning("GitHub Storage no está disponible. Usando almacenamiento local.")
            return False
        return True
        
    def save_file(self, file, path):
        """Guarda un archivo en el repositorio"""
        if not self._check_initialization():
            return False
            
        try:
            # Crear directorios necesarios
            full_path = os.path.join(self.temp_dir, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Guardar archivo
            if file:
                # Si es un archivo de Flask, guardarlo
                file.save(full_path)
            else:
                # Crear archivo vacío
                with open(full_path, 'w') as f:
                    f.write('')
            
            # Asegurarse que el archivo existe
            if not os.path.exists(full_path):
                logger.error(f"El archivo no se guardó correctamente: {full_path}")
                return False
                    
            # Añadir y hacer commit
            try:
                # Añadir el archivo al índice
                self.repo.index.add([path])
                
                # Hacer commit
                self.repo.index.commit(f"Actualización automática: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Push al repositorio
                origin = self.repo.remote(name='origin')
                origin.push()
                
                logger.info(f"Archivo guardado exitosamente: {path}")
                return True
            except Exception as e:
                logger.error(f"Error al hacer commit y push: {str(e)}")
                # Intentar hacer pull antes de push
                try:
                    origin = self.repo.remote(name='origin')
                    origin.pull()
                    # Intentar push nuevamente
                    origin.push()
                    logger.info(f"Archivo guardado exitosamente después de pull: {path}")
                    return True
                except Exception as e2:
                    logger.error(f"Error al hacer pull y push: {str(e2)}")
                    return False
            
        except Exception as e:
            logger.error(f"Error al guardar archivo: {str(e)}")
            return False
            
    def get_file(self, path):
        """Obtiene un archivo del repositorio"""
        if not self._check_initialization():
            return None
            
        try:
            full_path = os.path.join(self.temp_dir, path)
            if os.path.exists(full_path):
                return full_path
            return None
        except Exception as e:
            logger.error(f"Error al obtener archivo: {str(e)}")
            return None
            
    def list_files(self, path=''):
        """Lista archivos en el repositorio"""
        if not self._check_initialization():
            return []
            
        try:
            # Hacer pull para obtener los últimos cambios
            try:
                origin = self.repo.remote(name='origin')
                origin.pull()
            except Exception as e:
                logger.error(f"Error al hacer pull: {str(e)}")
            
            full_path = os.path.join(self.temp_dir, path)
            if not os.path.exists(full_path):
                logger.warning(f"La ruta {full_path} no existe")
                return []
                
            # Obtener solo los directorios
            carpetas = []
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                if os.path.isdir(item_path) and item != '1' and item != '.git':  # Excluir la carpeta '1' y '.git'
                    # Verificar si la carpeta contiene archivos PDF
                    pdf_count = len([f for f in os.listdir(item_path) if f.lower().endswith('.pdf')])
                    if pdf_count > 0:  # Solo incluir carpetas que contengan PDFs
                        carpetas.append(item)
            
            logger.info(f"Listadas {len(carpetas)} carpetas en {path}: {carpetas}")
            return carpetas
        except Exception as e:
            logger.error(f"Error al listar archivos: {str(e)}")
            return []
            
    def delete_file(self, path):
        """Elimina un archivo del repositorio"""
        if not self._check_initialization():
            return False
            
        try:
            full_path = os.path.join(self.temp_dir, path)
            if os.path.exists(full_path):
                os.remove(full_path)
                self.repo.index.remove([path])
                self.repo.index.commit(f"Eliminación automática: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Push al repositorio
                origin = self.repo.remote(name='origin')
                origin.push()
                
                logger.info(f"Archivo eliminado exitosamente: {path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {str(e)}")
            return False

# Instancia global del almacenamiento GitHub
github_storage = GitHubStorage() 