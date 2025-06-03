import os
import logging
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

class S3Storage:
    def __init__(self):
        try:
            # Verificar que las variables de entorno necesarias estén configuradas
            required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_BUCKET_NAME']
            missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
            
            if missing_vars:
                logger.warning(f"Variables de entorno faltantes para S3: {', '.join(missing_vars)}")
                self.s3_client = None
                self.bucket_name = None
                return

            # Inicializar el cliente S3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_REGION', 'us-east-1')
            )
            self.bucket_name = os.environ.get('AWS_BUCKET_NAME')
            
            # Verificar que el bucket existe
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                logger.info(f"Cliente S3 inicializado correctamente con bucket: {self.bucket_name}")
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    logger.error(f"El bucket {self.bucket_name} no existe")
                elif error_code == '403':
                    logger.error(f"No hay acceso al bucket {self.bucket_name}")
                else:
                    logger.error(f"Error al verificar el bucket: {str(e)}")
                self.s3_client = None
                self.bucket_name = None
                
        except Exception as e:
            logger.error(f"Error al inicializar S3 Storage: {str(e)}")
            self.s3_client = None
            self.bucket_name = None
        
    def _check_initialization(self):
        """Verifica si el cliente S3 está inicializado correctamente"""
        if not self.s3_client or not self.bucket_name:
            logger.error("Cliente S3 no inicializado correctamente")
            return False
        return True
        
    def upload_file(self, file_path, s3_key):
        """Sube un archivo a S3"""
        if not self._check_initialization():
            return False
            
        try:
            if not os.path.exists(file_path):
                logger.error(f"El archivo {file_path} no existe")
                return False
                
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            logger.info(f"Archivo {file_path} subido exitosamente a {s3_key}")
            return True
        except ClientError as e:
            logger.error(f"Error al subir archivo a S3: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al subir archivo: {str(e)}")
            return False
            
    def download_file(self, s3_key, local_path):
        """Descarga un archivo de S3"""
        if not self._check_initialization():
            return False
            
        try:
            # Crear el directorio si no existe
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            logger.info(f"Archivo {s3_key} descargado exitosamente a {local_path}")
            return True
        except ClientError as e:
            logger.error(f"Error al descargar archivo de S3: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al descargar archivo: {str(e)}")
            return False
            
    def list_files(self, prefix=''):
        """Lista archivos en S3 con un prefijo específico"""
        if not self._check_initialization():
            return []
            
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            files = [obj['Key'] for obj in response.get('Contents', [])]
            logger.info(f"Listados {len(files)} archivos con prefijo {prefix}")
            return files
        except ClientError as e:
            logger.error(f"Error al listar archivos en S3: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado al listar archivos: {str(e)}")
            return []
            
    def delete_file(self, s3_key):
        """Elimina un archivo de S3"""
        if not self._check_initialization():
            return False
            
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"Archivo {s3_key} eliminado exitosamente")
            return True
        except ClientError as e:
            logger.error(f"Error al eliminar archivo de S3: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al eliminar archivo: {str(e)}")
            return False
            
    def get_file_url(self, s3_key, expiration=3600):
        """Genera una URL temporal para acceder al archivo"""
        if not self._check_initialization():
            return None
            
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            logger.info(f"URL generada para {s3_key} con expiración de {expiration} segundos")
            return url
        except ClientError as e:
            logger.error(f"Error al generar URL de S3: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al generar URL: {str(e)}")
            return None

# Instancia global del almacenamiento S3
s3_storage = S3Storage() 