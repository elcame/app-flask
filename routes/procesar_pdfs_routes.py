from flask import Blueprint, request, jsonify, send_from_directory, Response, stream_with_context, send_file, render_template
import os
from extensions.procesar_pdfs import procesar_pdfs_en_carpeta_para_post, pdf_to_text, extraer_datos, incrementar_contador
from extensions.utils import guardar_dato_no_procesado
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
import requests
import re
import shutil
from flask_login import login_required, current_user
from extensions.github_storage import github_storage
import logging
import tempfile
import zipfile

procesar_pdfs_bp = Blueprint('procesar_pdfs_bp', __name__)
logger = logging.getLogger(__name__)

# Directorio base para almacenar archivos
if os.environ.get('RENDER'):
    UPLOAD_FOLDER = '/opt/render/project/src/uploads'
else:
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads'))

logger.info(f"UPLOAD_FOLDER configurado en: {UPLOAD_FOLDER}")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    logger.info(f"Carpeta UPLOAD_FOLDER creada en: {UPLOAD_FOLDER}")

# Diccionario global para almacenar los contadores individuales por placa
contadores_por_placa = {}

def incrementar_contador_local(placa):
    """
    Incrementa y devuelve el contador individual para la placa especificada.
    """
    global contadores_por_placa

    # Si la placa no está en el diccionario, inicializar su contador en 0
    if placa not in contadores_por_placa:
        contadores_por_placa[placa] = 0

    # Incrementar el contador para la placa
    contadores_por_placa[placa] += 1

    # Devolver el valor actualizado del contador
    return contadores_por_placa[placa]

@procesar_pdfs_bp.route('/subir_carpeta', methods=['POST'])
def subir_carpeta():
    try:
        logger.info("Iniciando subida de carpeta...")
        logger.info(f"Directorio base UPLOAD_FOLDER: {UPLOAD_FOLDER}")
        logger.info(f"Contenido actual de UPLOAD_FOLDER: {os.listdir(UPLOAD_FOLDER)}")
        
        if 'folder' not in request.files:
            logger.error("No se encontraron archivos en la petición")
            return jsonify({'error': 'No se ha enviado ningún archivo'}), 400
            
        archivos = request.files.getlist('folder')
        if not archivos:
            logger.error("La lista de archivos está vacía")
            return jsonify({'error': 'No se han seleccionado archivos'}), 400
            
        # Crear nombre de carpeta con timestamp
        timestamp = datetime.now().strftime('%d-%m-%Y')
        carpeta_destino = os.path.join(UPLOAD_FOLDER, timestamp)
        
        logger.info(f"Creando carpeta destino: {carpeta_destino}")
        logger.info(f"Ruta absoluta de la carpeta destino: {os.path.abspath(carpeta_destino)}")
        
        # Asegurarse que la carpeta existe
        os.makedirs(carpeta_destino, exist_ok=True)
        logger.info(f"Carpeta creada. Contenido de la carpeta: {os.listdir(carpeta_destino)}")
        
        # Contar PDFs y archivos guardados
        pdf_count = 0
        archivos_guardados = []
        
        # Guardar cada archivo
        for archivo in archivos:
            if archivo.filename.lower().endswith('.pdf'):
                filename = secure_filename(archivo.filename)
                ruta_completa = os.path.join(carpeta_destino, filename)
                logger.info(f"Guardando archivo: {ruta_completa}")
                logger.info(f"Ruta absoluta del archivo: {os.path.abspath(ruta_completa)}")
                
                try:
                    # Guardar localmente primero
                    archivo.save(ruta_completa)
                    
                    # Verificar que el archivo se guardó correctamente
                    if not os.path.exists(ruta_completa):
                        logger.error(f"El archivo no se guardó correctamente en: {ruta_completa}")
                        continue
                    else:
                        logger.info(f"Archivo guardado correctamente. Tamaño: {os.path.getsize(ruta_completa)} bytes")
                    
                    # Si estamos usando GitHub Storage, guardar también allí
                    if github_storage and github_storage.initialized:
                        try:
                            # Construir la ruta para GitHub
                            github_path = f'uploads/{timestamp}/{filename}'
                            logger.info(f"Intentando guardar en GitHub: {github_path}")
                            
                            # Crear una copia del archivo para GitHub
                            with open(ruta_completa, 'rb') as f:
                                archivo_copia = type('FileStorage', (), {'filename': filename, 'save': lambda path: shutil.copy2(ruta_completa, path)})
                                # Guardar en GitHub
                                if github_storage.save_file(archivo_copia, github_path):
                                    logger.info(f"Archivo guardado en GitHub: {github_path}")
                                else:
                                    logger.error(f"Error al guardar en GitHub: {github_path}")
                        except Exception as e:
                            logger.error(f"Error al guardar en GitHub: {str(e)}")
                    
                    pdf_count += 1
                    archivos_guardados.append(filename)
                except Exception as e:
                    logger.error(f"Error al guardar archivo {filename}: {str(e)}")
                    continue
        
        # Verificar que se guardaron archivos
        if pdf_count == 0:
            logger.error("No se guardó ningún archivo PDF")
            return jsonify({'error': 'No se pudo guardar ningún archivo PDF'}), 500
            
        # Mostrar contenido final de la carpeta
        logger.info(f"Contenido final de la carpeta {carpeta_destino}: {os.listdir(carpeta_destino)}")
        logger.info(f"Se subieron {pdf_count} archivos PDF correctamente")
        
        # Verificar que los archivos existen físicamente
        for archivo in archivos_guardados:
            ruta_archivo = os.path.join(carpeta_destino, archivo)
            if os.path.exists(ruta_archivo):
                logger.info(f"Archivo verificado: {ruta_archivo} - Tamaño: {os.path.getsize(ruta_archivo)} bytes")
            else:
                logger.error(f"Archivo no encontrado: {ruta_archivo}")
        
        return jsonify({
            'mensaje': f'Se subieron {pdf_count} archivos PDF correctamente',
            'carpeta': timestamp,
            'archivos': archivos_guardados,
            'ruta': carpeta_destino
        }), 200
        
    except Exception as e:
        logger.error(f"Error al subir carpeta: {str(e)}")
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/listar_carpetas', methods=['GET'])
def listar_carpetas():
    try:
        carpetas = []
        
        # Obtener carpetas del almacenamiento local
        carpetas_locales = []
        logger.info(f"Buscando carpetas en: {UPLOAD_FOLDER}")
        logger.info(f"Contenido de UPLOAD_FOLDER: {os.listdir(UPLOAD_FOLDER)}")
        
        # Función recursiva para buscar carpetas con PDFs
        def buscar_carpetas_con_pdfs(directorio, ruta_relativa=''):
            for item in os.listdir(directorio):
                ruta_completa = os.path.join(directorio, item)
                if os.path.isdir(ruta_completa):
                    # Contar PDFs en la carpeta actual
                    pdf_count = len([f for f in os.listdir(ruta_completa) if f.lower().endswith('.pdf')])
                    logger.info(f"Carpeta {ruta_completa} contiene {pdf_count} PDFs")
                    
                    if pdf_count > 0:
                        # Obtener fecha de creación
                        fecha = datetime.fromtimestamp(os.path.getctime(ruta_completa)).strftime('%Y-%m-%d %H:%M:%S')
                        # Si la carpeta está dentro de '1', solo usar el nombre de la carpeta
                        nombre_carpeta = item if '1' in ruta_relativa else os.path.join(ruta_relativa, item)
                        carpetas_locales.append({
                            'nombre': nombre_carpeta,
                            'pdfs': pdf_count,
                            'fecha': fecha,
                            'ruta': ruta_completa
                        })
                        logger.info(f"Carpeta {nombre_carpeta} añadida a la lista con {pdf_count} PDFs")
                    
                    # Buscar recursivamente en subcarpetas
                    buscar_carpetas_con_pdfs(ruta_completa, os.path.join(ruta_relativa, item))
        
        # Iniciar la búsqueda recursiva
        buscar_carpetas_con_pdfs(UPLOAD_FOLDER)
        
        # Ordenar carpetas por fecha (más recientes primero)
        carpetas = sorted(carpetas_locales, key=lambda x: x['fecha'], reverse=True)
        
        logger.info(f"Carpetas encontradas: {len(carpetas)}")
        logger.info(f"Lista de carpetas: {[c['nombre'] for c in carpetas]}")
        return jsonify(carpetas), 200
    except Exception as e:
        logger.error(f"Error al listar carpetas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/descargar_carpeta/<nombre>', methods=['GET'])
def descargar_carpeta(nombre):
    try:
        # Construir la ruta completa de la carpeta (dentro de la carpeta '1')
        carpeta = os.path.join(UPLOAD_FOLDER, '1', nombre)
        logger.info(f"Intentando descargar carpeta: {carpeta}")
        
        # Verificar si la carpeta existe
        if not os.path.exists(carpeta):
            logger.error(f"Carpeta no encontrada: {carpeta}")
            return jsonify({'error': 'Carpeta no encontrada'}), 404
            
        # Verificar que la carpeta contiene PDFs
        pdfs = [f for f in os.listdir(carpeta) if f.lower().endswith('.pdf')]
        if not pdfs:
            logger.error(f"La carpeta no contiene PDFs: {carpeta}")
            return jsonify({'error': 'La carpeta no contiene PDFs'}), 400
            
        # Crear un archivo ZIP temporal
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        logger.info(f"Archivo ZIP temporal creado: {temp_zip.name}")
        
        # Crear el archivo ZIP
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Agregar todos los archivos de la carpeta al ZIP
            for root, dirs, files in os.walk(carpeta):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, carpeta)
                    zipf.write(file_path, arcname)
                    logger.info(f"Archivo añadido al ZIP: {file_path}")
        
        # Enviar el archivo ZIP
        logger.info(f"Enviando archivo ZIP: {temp_zip.name}")
        return send_file(
            temp_zip.name,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'{nombre}.zip'
        )
    except Exception as e:
        logger.error(f"Error al descargar carpeta: {str(e)}")
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/cerrar_archivos/<nombre>', methods=['POST'])
def cerrar_archivos(nombre):
    try:
        # Construir la ruta completa de la carpeta
        carpeta = os.path.join(UPLOAD_FOLDER, nombre)
        
        # Verificar si la carpeta existe
        if not os.path.exists(carpeta):
            return jsonify({'error': 'Carpeta no encontrada'}), 404
            
        # Intentar cerrar todos los archivos en la carpeta
        for root, dirs, files in os.walk(carpeta):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    # Intentar abrir y cerrar el archivo para liberar cualquier handle
                    with open(file_path, 'rb') as f:
                        pass
                except Exception as e:
                    logger.warning(f"No se pudo cerrar el archivo {file_path}: {str(e)}")
                    continue
        
        return jsonify({'mensaje': 'Archivos cerrados correctamente'}), 200
    except Exception as e:
        logger.error(f"Error al cerrar archivos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/eliminar_carpeta/<nombre>', methods=['DELETE'])
def eliminar_carpeta(nombre):
    try:
        # Construir la ruta completa de la carpeta
        carpeta = os.path.join(UPLOAD_FOLDER, nombre)
        
        # Verificar si la carpeta existe
        if not os.path.exists(carpeta):
            return jsonify({'error': 'Carpeta no encontrada'}), 404
            
        # Intentar eliminar la carpeta y su contenido
        try:
            shutil.rmtree(carpeta)
        except PermissionError as e:
            logger.error(f"Error de permisos al eliminar carpeta: {str(e)}")
            # Intentar eliminar archivo por archivo
            for root, dirs, files in os.walk(carpeta, topdown=False):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        os.chmod(file_path, 0o777)  # Dar permisos completos
                        os.remove(file_path)
                    except Exception as e:
                        logger.error(f"No se pudo eliminar el archivo {file_path}: {str(e)}")
                for dir in dirs:
                    try:
                        dir_path = os.path.join(root, dir)
                        os.chmod(dir_path, 0o777)  # Dar permisos completos
                        os.rmdir(dir_path)
                    except Exception as e:
                        logger.error(f"No se pudo eliminar el directorio {dir_path}: {str(e)}")
            # Intentar eliminar la carpeta principal
            try:
                os.chmod(carpeta, 0o777)  # Dar permisos completos
                os.rmdir(carpeta)
            except Exception as e:
                logger.error(f"No se pudo eliminar la carpeta principal {carpeta}: {str(e)}")
                raise
        
        # Si estamos usando GitHub Storage, también eliminar del repositorio
        if github_storage and github_storage.initialized:
            try:
                github_storage.delete_file(f'uploads/{nombre}')
            except Exception as e:
                logger.error(f"Error al eliminar carpeta en GitHub: {str(e)}")
        
        return jsonify({'mensaje': 'Carpeta eliminada correctamente'}), 200
    except Exception as e:
        logger.error(f"Error al eliminar carpeta: {str(e)}")
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/ver_pdf/<path:filename>')
def ver_pdf(filename):
    try:
        # Asegurarse de que la ruta comience con 'uploads'
        if not filename.startswith('uploads/'):
            filename = f'uploads/{filename}'
            
        # Construir la ruta completa al archivo
        if os.environ.get('RENDER'):
            ruta_completa = os.path.join('/opt/render/project/src', filename)
        else:
            ruta_completa = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
            
        print(f"Intentando abrir PDF en: {ruta_completa}")
        
        # Verificar si el directorio existe
        directorio = os.path.dirname(ruta_completa)
        if not os.path.exists(directorio):
            print(f"El directorio no existe: {directorio}")
            os.makedirs(directorio, exist_ok=True)
            print(f"Directorio creado: {directorio}")
        
        if not os.path.exists(ruta_completa):
            print(f"Archivo no encontrado: {ruta_completa}")
            return jsonify({'error': 'Archivo no encontrado'}), 404
            
        return send_file(ruta_completa, mimetype='application/pdf')
    except Exception as e:
        print(f"Error al ver PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/procesar-pdfs')
@login_required
def procesar_pdfs():
    try:
        # Obtener la lista de carpetas desde GitHub
        folders = github_storage.list_files('uploads')
        return render_template('procesar_pdfs.html', folders=folders)
    except Exception as e:
        logger.error(f"Error al listar carpetas: {str(e)}")
        return render_template('procesar_pdfs.html', folders=[])

@procesar_pdfs_bp.route('/obtener-carpetas-uploads')
@login_required
def obtener_carpetas_uploads():
    try:
        # Obtener la lista de carpetas desde GitHub
        folders = github_storage.list_files('uploads')
        return jsonify({'success': True, 'folders': folders})
    except Exception as e:
        logger.error(f"Error al obtener carpetas: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@procesar_pdfs_bp.route('/subir-pdf', methods=['POST'])
@login_required
def subir_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'success': False, 'error': 'No se encontró el archivo'})
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó ningún archivo'})
        
        if file and file.filename.endswith('.pdf'):
            # Crear estructura de carpetas
            company_id = current_user.company_id
            fecha = datetime.now().strftime('%d-%m-%Y')
            folder_path = f'uploads/{company_id}/{fecha}'
            
            # Guardar archivo en GitHub
            filename = secure_filename(file.filename)
            file_path = f'{folder_path}/{filename}'
            github_storage.save_file(file, file_path)
            
            return jsonify({'success': True, 'message': 'Archivo subido correctamente'})
        else:
            return jsonify({'success': False, 'error': 'Solo se permiten archivos PDF'})
    except Exception as e:
        logger.error(f"Error al subir PDF: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@procesar_pdfs_bp.route('/descargar-pdf/<path:file_path>')
@login_required
def descargar_pdf(file_path):
    try:
        # Obtener archivo desde GitHub
        file_content = github_storage.get_file(file_path)
        if file_content:
            return send_file(
                file_content,
                as_attachment=True,
                download_name=os.path.basename(file_path)
            )
        return jsonify({'success': False, 'error': 'Archivo no encontrado'})
    except Exception as e:
        logger.error(f"Error al descargar PDF: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@procesar_pdfs_bp.route('/datos_procesados', methods=['GET'])
def mostrar_datos_procesados():
    try:
        datos = obtener_datos_procesados()
        if not datos:
            return jsonify([]), 200
            
        # Formatear los datos para la tabla
        datos_formateados = []
        for dato in datos:
            datos_formateados.append({
                'id': dato.get('ID', ''),
                'placa': dato.get('PLACA', ''),
                'conductor': dato.get('CONDUCTOR', ''),
                'origen': dato.get('ORIGEN', ''),
                'destino': dato.get('DESTINO', ''),
                'fecha': dato.get('FECHA', ''),
                'mes': dato.get('MES', ''),
                'kof': dato.get('KOF', ''),
                'remesa': dato.get('REMESA', ''),
                'empresa': dato.get('EMPRESA', ''),
                'valor_flete': dato.get('VALOR_FLETE', ''),
                'pdf_path': dato.get('PDF_PATH', '')
            })
        return jsonify(datos_formateados), 200
    except Exception as e:
        print(f"Error al obtener datos procesados: {e}")
        return jsonify({'error': str(e)}), 500

def obtener_datos_procesados():
    try:
        # Verificar si el archivo existe
        if not os.path.exists('datos_procesados.json'):
            return []
            
        # Leer el archivo
        with open('datos_procesados.json', 'r', encoding='utf-8') as archivo_json:
            try:
                datos = json.load(archivo_json)
                return datos
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON: {str(e)}")
                # Si hay error, intentar reparar el archivo
                try:
                    # Leer el contenido como texto
                    archivo_json.seek(0)
                    contenido = archivo_json.read()
                    # Limpiar el contenido de posibles caracteres extra
                    contenido = contenido.strip()
                    # Buscar el último corchete válido
                    ultimo_corchete = contenido.rfind(']')
                    if ultimo_corchete != -1:
                        contenido = contenido[:ultimo_corchete + 1]
                    # Intentar parsear el JSON limpio
                    datos = json.loads(contenido)
                    # Guardar el JSON limpio
                    with open('datos_procesados.json', 'w', encoding='utf-8') as f:
                        json.dump(datos, f, indent=4, ensure_ascii=False)
                    return datos
                except Exception as e2:
                    print(f"Error al reparar el archivo JSON: {str(e2)}")
                    # Si no se puede reparar, crear un nuevo archivo vacío
                    with open('datos_procesados.json', 'w', encoding='utf-8') as f:
                        json.dump([], f)
                    return []
    except Exception as e:
        print(f"Error al obtener datos procesados: {str(e)}")
        return []

@procesar_pdfs_bp.route('/uploads/<path:filename>')
def serve_uploads(filename):
    try:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@procesar_pdfs_bp.route('/datos_no_procesados')
def obtener_datos_no_procesados():
    try:
        archivo_json = os.path.join('datos_no_procesados', 'datos_no_procesados.json')
        if not os.path.exists(archivo_json):
            return jsonify([])
            
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            
        return jsonify(datos)
    except Exception as e:
        print(f"Error al obtener datos no procesados: {str(e)}")
        return jsonify([])

@procesar_pdfs_bp.route('/datos_no_procesados/<id>', methods=['GET'])
def obtener_dato_no_procesado(id):
    try:
        # Ruta correcta del archivo JSON
        archivo_json = 'datos_no_procesados/datos_no_procesados.json'
        
        if not os.path.exists(archivo_json):
            return jsonify({'error': 'No se encontró el archivo de datos no procesados'}), 404
            
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            
        # Buscar el dato por ID
        for dato in datos:
            if dato.get('ID') == id:
                return jsonify(dato), 200
                
        return jsonify({'error': 'Dato no encontrado'}), 404
        
    except Exception as e:
        print(f"Error al obtener dato no procesado: {str(e)}")
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/datos_no_procesados/<id>', methods=['PUT'])
def actualizar_dato_no_procesado(id):
    try:
        data = request.get_json()
        with open('datos_no_procesados.json', 'r', encoding='utf-8') as archivo_json:
            datos = json.load(archivo_json)
        
        for dato in datos:
            if dato.get('ID') == id:
                # Actualizar solo los campos que vienen en la petición
                for key, value in data.items():
                    if value:  # Solo actualizar si el valor no está vacío
                        dato[key.upper()] = value
                
                with open('datos_no_procesados.json', 'w', encoding='utf-8') as archivo_json:
                    json.dump(datos, archivo_json, ensure_ascii=False, indent=4)
                return jsonify({'message': 'Dato actualizado correctamente'}), 200
                
        return jsonify({'error': 'Dato no encontrado'}), 404
    except Exception as e:
        print(f"Error al actualizar dato no procesado: {e}")
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/datos_procesados/<id>', methods=['GET'])
def obtener_dato_procesado(id):
    try:
        with open('datos_procesados.json', 'r', encoding='utf-8') as archivo_json:
            datos = json.load(archivo_json)
            dato = next((d for d in datos if d.get('ID') == id), None)
            if dato:
                # Solo devolver los campos necesarios
                return jsonify({
                    'id': dato.get('ID', ''),
                    'placa': dato.get('PLACA', ''),
                    'conductor': dato.get('CONDUCTOR', ''),
                    'origen': dato.get('ORIGEN', ''),
                    'destino': dato.get('DESTINO', ''),
                    'fecha': dato.get('FECHA', ''),
                    'mes': dato.get('MES', ''),
                    'kof': dato.get('KOF', ''),
                    'remesa': dato.get('REMESA', ''),
                    'empresa': dato.get('EMPRESA', ''),
                    'valor_flete': dato.get('VALOR_FLETE', ''),
                    'pdf_path': dato.get('PDF_PATH', '')
                }), 200
            return jsonify({'error': 'Dato no encontrado'}), 404
    except FileNotFoundError:
        return jsonify({'error': 'No hay datos procesados'}), 404
    except Exception as e:
        print(f"Error al obtener dato procesado: {e}")
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/datos_procesados/<id>', methods=['PUT'])
def actualizar_dato_procesado(id):
    try:
        data = request.get_json()
        with open('datos_procesados.json', 'r', encoding='utf-8') as archivo_json:
            datos = json.load(archivo_json)
        
        for dato in datos:
            if dato.get('ID') == id:
                # Actualizar solo los campos que vienen en la petición
                for key, value in data.items():
                    if value:  # Solo actualizar si el valor no está vacío
                        dato[key.upper()] = value
                
                with open('datos_procesados.json', 'w', encoding='utf-8') as archivo_json:
                    json.dump(datos, archivo_json, ensure_ascii=False, indent=4)
                return jsonify({'message': 'Dato actualizado correctamente'}), 200
                
        return jsonify({'error': 'Dato no encontrado'}), 404
    except Exception as e:
        print(f"Error al actualizar dato procesado: {e}")
        return jsonify({'error': str(e)}), 500

def obtener_dato_procesado_por_id(id):
    try:
        with open('datos_procesados.json', 'r', encoding='utf-8') as archivo_json:
            datos = json.load(archivo_json)
            return next((d for d in datos if d.get('ID') == id), None)
    except Exception as e:
        print(f"Error al obtener dato procesado: {e}")
        return None

def actualizar_dato_procesado_por_id(id, data):
    try:
        with open('datos_procesados.json', 'r', encoding='utf-8') as archivo_json:
            datos = json.load(archivo_json)
        
        for dato in datos:
            if dato.get('ID') == id:
                # Actualizar solo los campos que vienen en la petición
                for key, value in data.items():
                    if value:  # Solo actualizar si el valor no está vacío
                        dato[key.upper()] = value
                
                with open('datos_procesados.json', 'w', encoding='utf-8') as archivo_json:
                    json.dump(datos, archivo_json, ensure_ascii=False, indent=4)
                return True
        return False
    except Exception as e:
        print(f"Error al actualizar dato procesado: {e}")
        return False

def procesar_pdf(archivo, carpeta_destino):
    try:
        print(f"Procesando archivo: {archivo}")
        ruta_completa = os.path.join(carpeta_destino, archivo)
        print(f"Ruta completa del archivo: {ruta_completa}")
        
        # Extraer fecha del nombre del archivo
        fecha_match = re.search(r'(\d{2}-\d{2}-\d{4})', archivo)
        if not fecha_match:
            print(f"No se encontró fecha en el nombre del archivo: {archivo}")
            return None
            
        fecha_actual = fecha_match.group(1)
        print(f"Fecha extraída: {fecha_actual}")
        
        # Extraer ID y placa del nombre del archivo
        match = re.search(r'global\s+(\w+)\s+ID\s+(\d+)', archivo)
        if match:
            placa = match.group(1)
            id_num = match.group(2)
            print(f"Placa extraída: {placa}, ID extraído: {id_num}")
            
            # Construir la ruta del PDF relativa a la carpeta uploads
            pdf_path = f"{fecha_actual}/global {placa} ID {id_num}.pdf"
            print(f"Ruta del PDF construida: {pdf_path}")
            
            # Crear el manifiesto con la ruta del PDF
            manifiesto = {
                'NUMERO': id_num,
                'PLACA': placa,
                'CONDUCTOR': '',
                'ORIGEN': '',
                'DESTINO': '',
                'FECHA': fecha_actual,
                'MES': datetime.strptime(fecha_actual, '%d-%m-%Y').strftime('%B'),
                'ID': id_num,
                'KOF': '',
                'REMESA': '',
                'EMPRESA': '',
                'VALOR_FLETE': 0,
                'PDF_PATH': pdf_path  # Agregar la ruta del PDF
            }
            
            print(f"Manifiesto creado: {manifiesto}")
            return manifiesto
        else:
            print(f"No se encontró coincidencia en el nombre del archivo: {archivo}")
            return None
            
    except Exception as e:
        print(f"Error procesando PDF {archivo}: {str(e)}")
        return None