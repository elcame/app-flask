from flask import Blueprint, jsonify, send_file
import subprocess
import os
import tempfile
import tkinter as tk
from tkinter import filedialog
import fitz
import re
import pandas as pd

scan_bp = Blueprint('scan_bp', __name__)

def seleccionar_carpeta():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de Tkinter
    carpeta = filedialog.askdirectory(title="Seleccionar carpeta de destino")
    root.destroy()
    return carpeta

@scan_bp.route('/scan', methods=['GET'])
def scan_document():
    try:
        # Crear un archivo temporal para la imagen escaneada
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            image_path = temp_file.name

        # Ruta completa al archivo naps2.console.exe
        naps2_console_path = 'C:\\Program Files\\NAPS2\\naps2.console.exe'

        # Comando para escanear la imagen usando NAPS2
        scan_command = [
            naps2_console_path,
            '-o', image_path,
            '-f', 'pdf',
            '--dpi', '300'
        ]

        # Ejecutar el comando de escaneo
        result = subprocess.run(scan_command, capture_output=True, text=True)

        # Verificar si hubo algún error
        if result.returncode != 0:
            return jsonify({'error': result.stderr}), 500

        # Verificar si el archivo de salida se creó correctamente
        if not os.path.exists(image_path):
            return jsonify({'error': 'El archivo escaneado no se creó correctamente'}), 500

        # Permitir al usuario seleccionar la carpeta de destino
        output_folder = seleccionar_carpeta()
        if not output_folder:
            return jsonify({'error': 'No se seleccionó ninguna carpeta'}), 400

        # Guardar el archivo escaneado en la carpeta seleccionada
        output_path = os.path.join(output_folder, os.path.basename(image_path))
        os.rename(image_path, output_path)

        # Procesar el archivo escaneado
        procesar_pdfs_en_carpeta(output_folder, "datos_link.xlsx", "datos_excel.xlsx")

        # Enviar la imagen escaneada al cliente
        return send_file(output_path, mimetype='application/pdf')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def procesar_pdfs_en_carpeta(carpeta, archivo_excel, archivo_excel2):
    # Inicializar una lista para almacenar todos los datos de todos los PDFs
    todos_los_datos_LINK = []
    todos_los_datos_EXCEL = []
    # Inicializar un conjunto para almacenar todas las combinaciones únicas de PLACA y ID
    combinaciones_unicas = set()
    # Recorrer todos los archivos PDF en la carpeta
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".pdf"):
            ruta_pdf = os.path.join(carpeta, archivo)
            print(f"Procesando archivo: {ruta_pdf}")

            # Extraer el texto del PDF
            texto_extraido = pdf_to_text(ruta_pdf)

            if texto_extraido:
                # Extraer los datos del texto
                datos_pdf = extraer_datos(texto_extraido)
                lista_datos_link = datos_pdf[0]
                lista_datos_excel = datos_pdf[1]
                if lista_datos_link and lista_datos_excel:
                    # Renombrar los PDFs
                    placa = lista_datos_link[0]['PLACA'].replace(" ", "")
                    referencia = lista_datos_link[0]['ID'].replace(" ", "")
                    combinacion = (placa, referencia)
                    if combinacion not in combinaciones_unicas:
                        combinaciones_unicas.add(combinacion)
                        nuevo_nombre = f"global {placa} ID {referencia}.pdf"
                        nuevo_ruta_pdf = os.path.join(carpeta, nuevo_nombre)
                        os.rename(ruta_pdf, nuevo_ruta_pdf)
                        print(f"Archivo renombrado a: {nuevo_ruta_pdf}")

                        # Agregar los datos del PDF a la lista de todos los datos
                        todos_los_datos_LINK.extend(lista_datos_link)
                        todos_los_datos_EXCEL.extend(lista_datos_excel)
                    else:
                        print(f"Duplicado encontrado: {ruta_pdf} no será renombrado ni agregado.")
                else:
                    print(f"No se encontraron datos en el archivo: {ruta_pdf}")
            else:
                print(f"No se pudo extraer datos del archivo: {ruta_pdf}")
    # Convertir la lista de todos los datos en un DataFrame de pandas
    df_nuevos_datos2 = pd.DataFrame(todos_los_datos_EXCEL)
    df_nuevos_datos = pd.DataFrame(todos_los_datos_LINK)

    # Verificar si el archivo Excel ya existe
    try:
        # Leer el archivo Excel existente
        df_existente = pd.read_excel(archivo_excel)
        df_existente2 = pd.read_excel(archivo_excel2)
        # Concatenar los datos nuevos con los existentes
        df_final = pd.concat([df_existente, df_nuevos_datos], ignore_index=True)
        df_final2 = pd.concat([df_existente2, df_nuevos_datos2], ignore_index=True)
        print(f"Datos existentes leídos y concatenados. Total de filas ahora: {len(df_final)}")
        print(f"Datos existentes leídos y concatenados. Total de filas ahora: {len(df_final2)}")

    except FileNotFoundError:
        # Si el archivo no existe, simplemente usamos los nuevos datos
        df_final = df_nuevos_datos
        print("No se encontró un archivo Excel previo. Creando uno nuevo.")
        df_final2 = df_nuevos_datos2
        print("No se encontró un archivo Excel previo. Creando uno nuevo.")
    # Guardar el DataFrame final (con los datos anteriores y nuevos) en un archivo Excel
    df_final.to_excel(archivo_excel, index=False)
    print(f"Datos guardados en '{archivo_excel}'.")
    df_final2.to_excel(archivo_excel2, index=False)
    print(f"Datos guardados en '{archivo_excel2}'.")

def pdf_to_text(ruta_pdf):
    if not os.path.exists(ruta_pdf):
        raise FileNotFoundError(f"No such file: '{ruta_pdf}'")
    doc = fitz.open(ruta_pdf)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def extraer_datos(texto_extraido):
    # Expresiones regulares para extraer la información
    palabraclave1 = r'\s*Fecha\s*: (.*)Hora'
    palabraclave2 = r' Hora\s*: (.*)'
    palabraclave3 = r'LOAD ID #(.*)'
    palabraclave4 = r'\s*CONDUCTOR\s*: (.*)'
    palabraclave5 = r'\s*PLACA\s*:\s*([A-Za-z0-9]+)'
    palabraclave6 = r'\s*6(?!01747000|01252548\d)\d{8}'
    palabraclave7 = r'\s*REMESA No\.\s*(KBQ[0-9]+)'
    palabraclave8 = r'P?[E-e]xp\.\s*(.*?)\s*\('

    # Buscar la información en el texto
    fecha = re.findall(palabraclave1, texto_extraido)
    if fecha:
        fecha[0] = fecha[0].replace('.', '/')
    hora = re.findall(palabraclave2, texto_extraido)
    referencia = re.findall(palabraclave3, texto_extraido)
    conductor = re.findall(palabraclave4, texto_extraido)
    placa = re.findall(palabraclave5, texto_extraido)
    KOF = re.findall(palabraclave6, texto_extraido)
    destino = re.findall(palabraclave8, texto_extraido)
    print(destino)

    kof = [num for num in KOF]
    KBQ = re.findall(palabraclave7, texto_extraido)
    KBQ = [num for num in KBQ]

    remolque = determinar_remolque(placa[0] if placa else ' ')

    jornada = float(hora[0].split(':')[0]) if hora else 0
    jornada = int(jornada)
    jornada = 'NOCTURNA' if jornada < 6 or jornada > 18 else 'DIURNA'

    origen = 'BARRANQUILLA'
    destino_final = destino[0] if destino else ' '
    lista_de_datos = []  # Inicializar la lista
    lista_de_EXCEL = []  # Inicializar la lista EXCEL
    jornadaretorno = None
    if len(hora) > 1:
        jornadaretorno = int(hora[1].split(':')[0])
        jornadaretorno = 'NOCTURNA' if jornadaretorno < 6 or jornadaretorno > 18 else 'DIURNA'
    
    agregar_datos_lista_link(lista_de_datos, fecha, conductor, placa, remolque, jornada, referencia, kof, origen, destino_final, jornadaretorno)
    agregar_datos_EXCEL(lista_de_EXCEL, placa, conductor, origen, destino_final, fecha, 'FEBRERO', referencia, kof, KBQ, 'CAMELO ARENAS GUILLERMO ANDRES')
    return lista_de_datos, lista_de_EXCEL

def determinar_remolque(placa):
    return "Remolque"

def agregar_datos_lista_link(lista_de_datos, fecha, conductor, placa, REMOLQUE, jornada, referencia, kof, origen, destino, jornadaretorno=None):
    if len(kof) < 2:
        valor = 250000
        datos_link = {
            'FECHA': fecha[0] if fecha else ' ',
            'CONDUCTOR': conductor[0] if conductor else ' ',
            'PLACA': placa[0] if placa else ' ',
            'REMOLQUE': REMOLQUE if REMOLQUE else ' ',
            'ORIGEN': origen,
            'DESTINO': destino,
            'JORNADA LABORAL': jornada,
            'ID': referencia[0] if referencia else ' ',
            'NOTA DE OPERACIÓN': kof[0] if kof else ' '
        }
        lista_de_datos.append(datos_link)
    else:
        valor = 280000
        datos_ida = {
            'FECHA': fecha[0] if fecha else ' ',
            'CONDUCTOR': conductor[0] if conductor else ' ',
            'PLACA': placa[0] if placa else ' ',
            'REMOLQUE': REMOLQUE if REMOLQUE else ' ',
            'ORIGEN': origen,
            'DESTINO': destino,
            'JORNADA LABORAL': jornada,
            'ID': referencia[0] if referencia else ' ',
            'NOTA DE OPERACIÓN': kof[0] if kof else ' '
        }
        lista_de_datos.append(datos_ida)

        if jornadaretorno is not None:
            datos_retorno = {
                'FECHA': fecha[0] if fecha else ' ',
                'CONDUCTOR': conductor[0] if conductor else ' ',
                'PLACA': placa[0] if placa else ' ',
                'REMOLQUE': REMOLQUE if REMOLQUE else ' ',
                'ORIGEN': destino,
                'DESTINO': origen,
                'JORNADA LABORAL': jornadaretorno,
                'ID': kof[1] if referencia else ' ',
                'NOTA DE OPERACIÓN': kof[1] if len(kof) > 1 else ' '
            }
            lista_de_datos.append(datos_retorno)

def agregar_datos_EXCEL(lista_de_datos, PLACA, CONDUCTOR, ORIGEN, DESTINO, FECHAVIAJE, MES, ID, KOF, REMESA, EMPRESA):
    # Determinar el valor del flete basado en la longitud de KOF
    if DESTINO == "Cartagena":
        valor = 1700000
    else:
        if len(KOF) < 2:
            valor = 250000
        else:
            valor = 280000

    # Crear el diccionario con los datos
    datos_excel = {
        'PLACA': PLACA[0] if PLACA else ' ',
        'CONDUCTOR': CONDUCTOR[0] if CONDUCTOR else ' ',
        'ORIGEN': ORIGEN,
        'DESTINO': DESTINO,
        'FECHA': FECHAVIAJE[0] if FECHAVIAJE else ' ',
        'MES': MES,
        'ID': ID[0] if ID else ' ',
        'KOF 1': KOF[0] if KOF else ' ',
        'REMESA': REMESA[0],
        'EMPRESA': EMPRESA,
        'VALOR_FLETE': valor
    }

    # Agregar el diccionario a la lista de datos
    lista_de_datos.append(datos_excel)