from flask import Blueprint, request, jsonify, send_from_directory
import os
from extensions.procesar_pdfs import procesar_pdfs_en_carpeta_para_post
import json
from datetime import datetime
from werkzeug.utils import secure_filename

procesar_pdfs_bp = Blueprint('procesar_pdfs_bp', __name__)

# Configuración de la carpeta de uploads
UPLOAD_FOLDER = os.path.join('uploads', '1')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@procesar_pdfs_bp.route('/upload_folder', methods=['POST'])
def upload_folder():
    try:
        if 'folder' not in request.files:
            return jsonify({'error': 'No se ha enviado ningún archivo'}), 400

        files = request.files.getlist('folder')
        if not files:
            return jsonify({'error': 'No se han seleccionado archivos'}), 400

        # Crear una carpeta con la fecha actual
        fecha_actual = datetime.now().strftime('%d-%m-%Y')
        carpeta_destino = os.path.join(UPLOAD_FOLDER, fecha_actual)
        
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)

        # Guardar cada archivo en la carpeta
        for file in files:
            if file.filename.endswith('.pdf'):
                filename = secure_filename(file.filename)
                file.save(os.path.join(carpeta_destino, filename))

        return jsonify({'message': 'Carpeta subida correctamente'}), 200
    except Exception as e:
        print(f"Error al subir carpeta: {e}")
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/procesar_pdfs', methods=['POST'])
def procesar_pdfs():
    try:
        data = request.get_json()
        carpeta = data.get('carpeta')
        
        if not carpeta:
            return jsonify({'error': 'Faltan parámetros'}), 400
        
        print(f"Procesando PDFs en la carpeta: {carpeta}")
        ruta_completa = os.path.join(UPLOAD_FOLDER, carpeta)
        resultados = procesar_pdfs_en_carpeta_para_post(ruta_completa)
        return jsonify({'message': 'Procesamiento completado', 'resultados': resultados}), 200
    except Exception as e:
        print(f"Error al procesar PDFs: {e}")
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
        with open('datos_procesados.json', 'r', encoding='utf-8') as archivo_json:
            datos = json.load(archivo_json)
            return datos
    except FileNotFoundError:
        return []

@procesar_pdfs_bp.route('/carpetas_uploads', methods=['GET'])
def obtener_carpetas_uploads():
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            return jsonify([]), 200

        carpetas = []
        for carpeta in os.listdir(UPLOAD_FOLDER):
            ruta_completa = os.path.join(UPLOAD_FOLDER, carpeta)
            if os.path.isdir(ruta_completa):
                # Contar archivos PDF en la carpeta
                pdf_count = len([f for f in os.listdir(ruta_completa) if f.endswith('.pdf')])
                # Obtener fecha de modificación
                fecha_mod = os.path.getmtime(ruta_completa)
                fecha = datetime.fromtimestamp(fecha_mod).strftime('%Y-%m-%d %H:%M:%S')
                
                carpetas.append({
                    'nombre': carpeta,
                    'pdf_count': pdf_count,
                    'date': fecha
                })
        
        return jsonify(carpetas), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@procesar_pdfs_bp.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory('uploads', filename)