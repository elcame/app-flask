from flask import Blueprint, request, jsonify, send_from_directory, Response, stream_with_context, send_file
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

procesar_pdfs_bp = Blueprint('procesar_pdfs_bp', __name__)

# Directorio base para almacenar archivos
if os.environ.get('RENDER'):
    UPLOAD_FOLDER = '/opt/render/project/src/uploads'
else:
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
        print("Iniciando subida de carpeta...")  # Debug log
        
        if 'folder' not in request.files:
            print("No se encontraron archivos en la petición")  # Debug log
            return jsonify({'error': 'No se ha enviado ningún archivo'}), 400
            
        archivos = request.files.getlist('folder')
        if not archivos:
            print("La lista de archivos está vacía")  # Debug log
            return jsonify({'error': 'No se han seleccionado archivos'}), 400
            
        # Crear nombre de carpeta con timestamp
        timestamp = datetime.now().strftime('%d-%m-%Y')
        carpeta_destino = os.path.join(UPLOAD_FOLDER, timestamp)
        
        print(f"Creando carpeta destino: {carpeta_destino}")  # Debug log
        
        # Asegurarse que la carpeta existe
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)
            
        # Contar PDFs
        pdf_count = 0
        
        # Guardar cada archivo
        for archivo in archivos:
            if archivo.filename.lower().endswith('.pdf'):
                filename = secure_filename(archivo.filename)
                ruta_completa = os.path.join(carpeta_destino, filename)
                print(f"Guardando archivo: {ruta_completa}")  # Debug log
                archivo.save(ruta_completa)
                pdf_count += 1
                
        print(f"Se subieron {pdf_count} archivos PDF correctamente")  # Debug log
        return jsonify({
            'mensaje': f'Se subieron {pdf_count} archivos PDF correctamente',
            'carpeta': timestamp
        }), 200
        
    except Exception as e:
        print(f"Error al subir carpeta: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/listar_carpetas', methods=['GET'])
def listar_carpetas():
    try:
        carpetas = []
        for carpeta in os.listdir(UPLOAD_FOLDER):
            ruta_carpeta = os.path.join(UPLOAD_FOLDER, carpeta)
            if os.path.isdir(ruta_carpeta):
                # Contar PDFs en la carpeta
                pdf_count = len([f for f in os.listdir(ruta_carpeta) if f.lower().endswith('.pdf')])
                # Obtener fecha de creación
                fecha = datetime.fromtimestamp(os.path.getctime(ruta_carpeta)).strftime('%Y-%m-%d %H:%M:%S')
                carpetas.append({
                    'nombre': carpeta,
                    'pdfs': pdf_count,
                    'fecha': fecha
                })
        return jsonify(carpetas), 200
    except Exception as e:
        print(f"Error al listar carpetas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/eliminar_carpeta/<nombre>', methods=['DELETE'])
def eliminar_carpeta(nombre):
    try:
        carpeta = os.path.join(UPLOAD_FOLDER, nombre)
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)
            return jsonify({'mensaje': 'Carpeta eliminada correctamente'}), 200
        return jsonify({'error': 'Carpeta no encontrada'}), 404
    except Exception as e:
        print(f"Error al eliminar carpeta: {str(e)}")
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/ver_pdf/<path:filename>')
def ver_pdf(filename):
    try:
        # Asegurarse de que la ruta comience con 'uploads'
        if not filename.startswith('uploads/'):
            filename = f'uploads/{filename}'
            
        # Construir la ruta completa al archivo
        ruta_completa = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
        print(f"Intentando abrir PDF en: {ruta_completa}")
        
        if not os.path.exists(ruta_completa):
            print(f"Archivo no encontrado: {ruta_completa}")
            return jsonify({'error': 'Archivo no encontrado'}), 404
            
        return send_file(ruta_completa, mimetype='application/pdf')
    except Exception as e:
        print(f"Error al ver PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/procesar_pdfs', methods=['GET', 'POST'])
def procesar_pdfs():
    try:
        # Obtener la carpeta del query string si es GET o del JSON si es POST
        if request.method == 'GET':
            carpeta = request.args.get('carpeta')
        else:
            data = request.get_json()
            carpeta = data.get('carpeta')
        
        if not carpeta:
            return jsonify({'error': 'Faltan parámetros'}), 400
        
        print(f"Procesando PDFs en la carpeta: {carpeta}")
        ruta_completa = os.path.join(UPLOAD_FOLDER, carpeta)
        
        if not os.path.exists(ruta_completa):
            return jsonify({'error': 'La carpeta no existe'}), 404
        
        # Obtener lista de archivos PDF
        archivos_pdf = [f for f in os.listdir(ruta_completa) if f.lower().endswith('.pdf')]
        total_archivos = len(archivos_pdf)
        
        if total_archivos == 0:
            return jsonify({'error': 'No hay archivos PDF para procesar'}), 400
            
        def generate():
            try:
                # Enviar mensaje inicial
                yield f"data: {json.dumps({'progreso': 0, 'mensaje': 'Iniciando procesamiento...'})}\n\n"
                
                # Limpiar los archivos de datos procesados y no procesados al inicio
                with open('datos_procesados.json', 'w', encoding='utf-8') as archivo_json:
                    json.dump([], archivo_json, ensure_ascii=False, indent=4)
                with open('datos_no_procesados.json', 'w', encoding='utf-8') as archivo_json:
                    json.dump([], archivo_json, ensure_ascii=False, indent=4)
                
                # Procesar cada archivo individualmente
                for i, archivo in enumerate(archivos_pdf, 1):
                    try:
                        ruta_pdf = os.path.join(ruta_completa, archivo)
                        print(f"Procesando archivo {i}/{total_archivos}: {archivo}")
                        
                        # Construir la ruta del PDF para guardar
                        fecha_actual = datetime.now().strftime('%d-%m-%Y')
                        # Intentar extraer el ID y la placa del nombre del archivo
                        match = re.search(r'global\s+(\w+)\s+ID\s+(\d+)', archivo)
                        if match:
                            placa = match.group(1)
                            id_num = match.group(2)
                            pdf_path = f"{fecha_actual}/global {placa} ID {id_num}.pdf"
                        else:
                            pdf_path = f"{fecha_actual}/{archivo}"
                        
                        # Actualizar progreso inicial del archivo (0-30%)
                        progreso = int(((i-1)/total_archivos)*30)
                        yield f"data: {json.dumps({'progreso': progreso, 'mensaje': f'Iniciando procesamiento de {archivo} ({i}/{total_archivos})'})}\n\n"
                        
                        # Extraer texto del PDF
                        texto = pdf_to_text(ruta_pdf)
                        if not texto:
                            error = f"No se pudo extraer texto del PDF {archivo}"
                            
                            yield f"data: {json.dumps({'progreso': int((i/total_archivos)*30), 'mensaje': error})}\n\n"
                            continue
                            
                        # Actualizar progreso después de extraer texto (30-60%)
                        progreso = 30 + int(((i-0.5)/total_archivos)*30)
                        yield f"data: {json.dumps({'progreso': progreso, 'mensaje': f'Extrayendo datos de {archivo} ({i}/{total_archivos})'})}\n\n"
                            
                        # Extraer datos del texto
                        datos = extraer_datos(texto)
                        if not datos:
                            error = f"No se pudieron extraer datos del PDF {archivo}"
                           
                            yield f"data: {json.dumps({'progreso': int((i/total_archivos)*30), 'mensaje': error})}\n\n"
                            continue
                        
                        # Agregar la ruta del PDF
                        datos['PDF_PATH'] = pdf_path
                        
                        # Validar campos requeridos
                        campos_requeridos = ['ID', 'PLACA', 'CONDUCTOR', 'ORIGEN', 'DESTINO', 'FECHA']
                        campos_vacios = []
                        for campo in campos_requeridos:
                            if not datos.get(campo):
                                campos_vacios.append(campo)
                        
                        if campos_vacios:
                            error = f"Campos requeridos vacíos: {', '.join(campos_vacios)}"
                            # Solo guardar el error, no los datos parciales
                          
                            yield f"data: {json.dumps({'progreso': int((i/total_archivos)*30), 'mensaje': error})}\n\n"
                            continue
                        
                        # Guardar el dato procesado exitosamente
                        try:
                            with open('datos_procesados.json', 'r', encoding='utf-8') as archivo_json:
                                datos_procesados = json.load(archivo_json)
                        except (FileNotFoundError, json.JSONDecodeError):
                            datos_procesados = []
                        
                        datos_procesados.append(datos)
                        
                        with open('datos_procesados.json', 'w', encoding='utf-8') as archivo_json:
                            json.dump(datos_procesados, archivo_json, ensure_ascii=False, indent=4)
                        
                        # Actualizar progreso después de guardar datos (60-90%)
                        progreso = 60 + int(((i-0.5)/total_archivos)*30)
                        yield f"data: {json.dumps({'progreso': progreso, 'mensaje': f'Datos extraídos exitosamente ({i}/{total_archivos})'})}\n\n"
                        
                    except Exception as e:
                        print(f"Error al procesar archivo {archivo}: {str(e)}")
                        error = f"Error al procesar archivo: {str(e)}"
                      
                        yield f"data: {json.dumps({'progreso': int((i/total_archivos)*30), 'mensaje': error})}\n\n"
                
                # Procesar los datos para crear el Excel y enviar al endpoint (90-100%)
                try:
                    # Obtener el total de datos procesados
                    with open('datos_procesados.json', 'r', encoding='utf-8') as archivo_json:
                        datos_procesados = json.load(archivo_json)
                    total_datos = len(datos_procesados)
                    
                    # Actualizar progreso antes de crear Excel
                    yield f"data: {json.dumps({'progreso': 90, 'mensaje': 'Generando Excel y creando manifiestos...'})}\n\n"
                    
                    # Crear el Excel y enviar los datos al endpoint
                    procesar_pdfs_en_carpeta_para_post(ruta_completa)
                    
                    # Actualizar progreso final
                    yield f"data: {json.dumps({'progreso': 100, 'mensaje': f'¡Procesamiento completado! {total_datos} manifiestos creados correctamente.', 'completado': True})}\n\n"
                except Exception as e:
                    print(f"Error al generar Excel: {str(e)}")
                    yield f"data: {json.dumps({'progreso': 100, 'mensaje': f'Procesamiento completado con errores al generar Excel: {str(e)}', 'completado': True})}\n\n"
                
            except Exception as e:
                print(f"Error al procesar PDFs: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
        
    except Exception as e:
        print(f"Error al procesar PDFs: {str(e)}")
        return jsonify({'error': str(e)}), 500

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

@procesar_pdfs_bp.route('/carpetas_uploads', methods=['GET'])
def obtener_carpetas_uploads():
    try:
        print(f"Buscando carpetas en: {UPLOAD_FOLDER}")  # Debug log
        
        if not os.path.exists(UPLOAD_FOLDER):
            print(f"La carpeta {UPLOAD_FOLDER} no existe, creándola...")  # Debug log
            os.makedirs(UPLOAD_FOLDER)
            return jsonify([]), 200

        carpetas = []
        # Primero, buscar en la carpeta de la empresa 1
        empresa_folder = os.path.join(UPLOAD_FOLDER, '1')
        if os.path.exists(empresa_folder):
            print(f"Procesando carpeta de empresa: {empresa_folder}")  # Debug log
            # Listar las subcarpetas dentro de la carpeta de la empresa
            for subcarpeta in os.listdir(empresa_folder):
                ruta_subcarpeta = os.path.join(empresa_folder, subcarpeta)
                print(f"Procesando subcarpeta: {ruta_subcarpeta}")  # Debug log
                
                if os.path.isdir(ruta_subcarpeta):
                    # Contar archivos PDF en la subcarpeta
                    pdf_count = len([f for f in os.listdir(ruta_subcarpeta) if f.lower().endswith('.pdf')])
                    # Obtener fecha de modificación
                    fecha_mod = os.path.getmtime(ruta_subcarpeta)
                    fecha = datetime.fromtimestamp(fecha_mod).strftime('%Y-%m-%d %H:%M:%S')
                    
                    carpetas.append({
                        'nombre': subcarpeta,
                        'pdf_count': pdf_count,
                        'date': fecha
                    })
                    print(f"Subcarpeta encontrada: {subcarpeta} con {pdf_count} PDFs")  # Debug log
        
        print(f"Total de subcarpetas encontradas: {len(carpetas)}")  # Debug log
        return jsonify(carpetas), 200
    except Exception as e:
        print(f"Error al obtener carpetas: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

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