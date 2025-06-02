import os
import re
import pandas as pd
import fitz  # PyMuPDF
import requests
import json
import openpyxl  # Para manejo de archivos Excel
from datetime import datetime
from extensions.utils import guardar_dato_no_procesado  # Importar la función desde utils

# Variable global para el contador de numero
contador_numero = 0

def pdf_to_text(ruta_pdf):
    try:
        doc = fitz.open(ruta_pdf)
        texto = ""
        for pagina in doc:
            texto += pagina.get_text()
        doc.close()
        return texto
    except Exception as e:
        print(f"Error al extraer texto del PDF: {str(e)}")
        return None

def extraer_datos(texto_extraido):
    try:
        # Expresiones regulares para extraer la información
        palabraclave1 = r'\s*Fecha\s*: (.*)Hora'
        palabraclave2 = r' Hora\s*: (.*)'
        palabraclave3 = r'LOAD ID #(.*)'
        palabraclave4 = r'\s*CONDUCTOR\s*: (.*)'
        palabraclave5 = r'\s*PLACA\s*:\s*([A-Za-z0-9]+)'
        palabraclave6 = r'\s*6(?!01747000|01252548\d)\d{8}'
        palabraclave7 = r'(?i)\s*REMESA No\.\s*(KBQ[0-9]+)'
        palabraclave8 = r'P?[E-e]xp\.\s*(.*?)\s*\('

        # Buscar la información en el texto
        fecha = re.findall(palabraclave1, texto_extraido)
        hora = re.findall(palabraclave2, texto_extraido)
        referencia = re.findall(palabraclave3, texto_extraido)
        conductor = re.findall(palabraclave4, texto_extraido)
        placa = re.findall(palabraclave5, texto_extraido)
        KOF = re.findall(palabraclave6, texto_extraido)
        KBQ = re.findall(palabraclave7, texto_extraido)
        destino = re.findall(palabraclave8, texto_extraido)

        # Procesar la fecha y el mes
        if fecha:
            fecha[0] = fecha[0].replace('.', '/').strip()
            try:
                fecha_obj = datetime.strptime(fecha[0], '%d/%m/%Y')
                fecha[0] = fecha_obj.strftime('%Y-%m-%d')
                mes = fecha_obj.strftime('%B').upper()
            except ValueError:
                print(f"Fecha inválida: {fecha[0]}")
                fecha = [None]
                mes = 'DESCONOCIDO'
        else:
            fecha = [None]
            mes = 'DESCONOCIDO'

        # Validar y limpiar los datos
        placa = placa[0].strip() if placa else ''
        conductor = conductor[0].strip() if conductor else ''
        referencia = referencia[0].strip() if referencia else ''
        kof = KOF[0].strip() if KOF else ''
        remesa = KBQ[0].strip() if KBQ else ''
        destino_final = destino[0].strip() if destino else ''
        origen = 'BARRANQUILLA'

        # Determinar el valor del flete
        if destino_final.upper() == "CARTAGENA":
            valor_flete = 1700000
        else:
            valor_flete = 280000 if len(KOF) >= 2 else 250000

        # Obtener el número de manifiesto para la placa
        numero = incrementar_contador(placa)

        # Crear el diccionario con los datos procesados
        datos_procesados = {
            'ID': referencia if referencia else f'SIN_ID_{numero}',  # Aseguramos que siempre haya un ID
            'NUMERO': numero,
            'PLACA': placa,
            'CONDUCTOR': conductor,
            'ORIGEN': origen,
            'DESTINO': destino_final,
            'FECHA': fecha[0],
            'MES': mes,
            'KOF': kof,
            'REMESA': remesa,
            'EMPRESA': 'CAMELO ARENAS GUILLERMO ANDRES',
            'VALOR_FLETE': valor_flete
        }

        # Validar que los campos requeridos no estén vacíos
        campos_requeridos = ['ID', 'PLACA', 'CONDUCTOR', 'ORIGEN', 'DESTINO', 'FECHA']
        campos_vacios = []
        for campo in campos_requeridos:
            if not datos_procesados.get(campo):
                campos_vacios.append(campo)
        
        if campos_vacios:
            print(f"Campos requeridos vacíos: {', '.join(campos_vacios)}")
            # Crear una copia de los datos sin el campo error para datos procesados
            datos_procesados_sin_error = datos_procesados.copy()
            # Agregar el error solo para el retorno
            datos_procesados['error'] = f"Campos requeridos vacíos: {', '.join(campos_vacios)}"
            return datos_procesados

        return datos_procesados_sin_error if 'datos_procesados_sin_error' in locals() else datos_procesados

    except Exception as e:
        print(f"Error al extraer datos: {str(e)}")
        return None

def procesar_pdfs_en_carpeta_para_post(carpeta, url_post=None):
    try:
        # Si no se proporciona una URL, usar la URL del servidor actual
        if url_post is None:
            if os.environ.get('RENDER'):
                # En Render, usar la URL del servidor
                url_post = 'https://app-flask-5nh9.onrender.com/manifiestos'
            else:
                # En desarrollo local
                url_post = 'http://localhost:5000/manifiestos'

        # Inicializar una lista para almacenar todos los datos de todos los PDFs
        todos_los_datos_EXCEL = []
        # Inicializar un conjunto para almacenar todas las combinaciones únicas de PLACA y ID
        combinaciones_unicas = set()
        
        # Limpiar el archivo de datos procesados
        with open('datos_procesados.json', 'w', encoding='utf-8') as archivo_json:
            json.dump([], archivo_json, ensure_ascii=False, indent=4)
            
        # Crear directorio excel si no existe
        if not os.path.exists('excel'):
            os.makedirs('excel')
            
        # Obtener el nombre de la carpeta que se está procesando
        nombre_carpeta = os.path.basename(carpeta)
        
        # Crear directorio con el nombre de la carpeta si no existe
        directorio_excel = os.path.join('excel', nombre_carpeta)
        if not os.path.exists(directorio_excel):
            os.makedirs(directorio_excel)
            
        # Obtener el número de la empresa del nombre de la carpeta
        numero_empresa = nombre_carpeta.split('_')[0] if '_' in nombre_carpeta else '1'
        nombre_excel = f'{numero_empresa}_manifiestos.xlsx'
        ruta_excel = os.path.join(directorio_excel, nombre_excel)
        
        # Obtener lista de archivos PDF
        archivos_pdf = [f for f in os.listdir(carpeta) if f.lower().endswith('.pdf')]
        total_archivos = len(archivos_pdf)
        
        if total_archivos == 0:
            print("No hay archivos PDF para procesar.")
            return
        
        # Procesar cada archivo PDF
        for i, archivo in enumerate(archivos_pdf, 1):
            try:
                ruta_pdf = os.path.join(carpeta, archivo)
                subcarpeta = os.path.basename(carpeta)
                
                # Extraer el texto del PDF
                texto_extraido = pdf_to_text(ruta_pdf)
                
                if texto_extraido:
                    # Extraer los datos del texto
                    datos_pdf = extraer_datos(texto_extraido)
                    
                    if datos_pdf:
                        # Renombrar los PDFs
                        placa = datos_pdf['PLACA']
                        referencia = datos_pdf['ID']
                        combinacion = (placa, referencia)
                        if combinacion not in combinaciones_unicas:
                            combinaciones_unicas.add(combinacion)
                            nuevo_nombre = f"global {placa} ID {referencia}.pdf"
                            nuevo_ruta_pdf = os.path.join(carpeta, nuevo_nombre)
                            os.rename(ruta_pdf, nuevo_ruta_pdf)
                            
                            # Agregar la ruta del PDF a los datos
                            datos_pdf['PDF_PATH'] = f"/uploads/1/{subcarpeta}/{nuevo_nombre}"
                            
                            # Si hay error, guardar en datos no procesados
                            if 'error' in datos_pdf:
                                guardar_dato_no_procesado(datos_pdf, datos_pdf['error'])
                            else:
                                # Eliminar el campo error si existe antes de agregar a la lista
                                if 'error' in datos_pdf:
                                    del datos_pdf['error']
                                # Agregar los datos del PDF a la lista de todos los datos
                                todos_los_datos_EXCEL.append(datos_pdf)
                            
                            # Ya no mostramos progreso aquí
                            print(f"Procesando archivo {i} de {total_archivos}")
                        else:
                            print(f"Duplicado encontrado: {ruta_pdf} no será renombrado ni agregado.")
                    else:
                        # Si no se pudieron extraer los datos, guardar como no procesado
                        subcarpeta = os.path.basename(carpeta)
                        pdf_path = f"/uploads/1/{subcarpeta}/{archivo}"
                        
                        if datos_pdf and 'error' in datos_pdf:
                            # Si tenemos datos parciales con error, los usamos
                            datos_pdf['PDF_PATH'] = pdf_path
                            guardar_dato_no_procesado(datos_pdf, datos_pdf['error'])
                        else:
                            # Si no hay datos parciales, intentamos extraer del nombre del archivo
                            match = re.search(r'global\s+(\w+)\s+ID\s+(\d+)', archivo)
                            if match:
                                placa = match.group(1)
                                id_num = match.group(2)
                            else:
                                placa = "DESCONOCIDA"
                                id_num = f"SIN_ID_{incrementar_contador(placa)}"
                            
                            # Crear estructura de datos no procesados con los datos que se pudieron extraer
                            datos_no_procesados = {
                                'ID': id_num,
                                'NUMERO': incrementar_contador(placa),
                                'PLACA': placa,
                                'CONDUCTOR': 'SIN CONDUCTOR',
                                'ORIGEN': 'BARRANQUILLA',
                                'DESTINO': 'SIN DESTINO',
                                'FECHA': None,
                                'MES': 'DESCONOCIDO',
                                'KOF': 'SIN KOF',
                                'REMESA': 'SIN REMESA',
                                'EMPRESA': 'CAMELO ARENAS GUILLERMO ANDRES',
                                'VALOR_FLETE': 250000,
                                'PDF_PATH': pdf_path,
                                'error': "No se pudieron extraer los datos del PDF. Se extrajeron datos básicos del nombre del archivo."
                            }
                            guardar_dato_no_procesado(datos_no_procesados, "No se pudieron extraer los datos del PDF")
                else:
                    print(f"No se pudo extraer texto del archivo: {ruta_pdf}")
                    # Guardar la ruta del PDF incluso cuando no se puede procesar
                    subcarpeta = os.path.basename(carpeta)
                    pdf_path = f"/uploads/1/{subcarpeta}/{archivo}"
                    # Intentar extraer datos básicos del nombre del archivo
                    match = re.search(r'global\s+(\w+)\s+ID\s+(\d+)', archivo)
                    if match:
                        placa = match.group(1)
                        id_num = match.group(2)
                    else:
                        placa = "DESCONOCIDA"
                        id_num = f"SIN_ID_{incrementar_contador(placa)}"
                    
                    # Crear estructura de datos no procesados con los datos que se pudieron extraer
                    datos_no_procesados = {
                        'ID': id_num,
                        'NUMERO': incrementar_contador(placa),
                        'PLACA': placa,
                        'CONDUCTOR': 'SIN CONDUCTOR',
                        'ORIGEN': 'BARRANQUILLA',
                        'DESTINO': 'SIN DESTINO',
                        'FECHA': None,
                        'MES': 'DESCONOCIDO',
                        'KOF': 'SIN KOF',
                        'REMESA': 'SIN REMESA',
                        'EMPRESA': 'CAMELO ARENAS GUILLERMO ANDRES',
                        'VALOR_FLETE': 250000,
                        'PDF_PATH': pdf_path,
                        'error': f"No se pudo extraer texto del PDF {archivo}. Se extrajeron datos básicos del nombre del archivo."
                    }
                    guardar_dato_no_procesado(datos_no_procesados, f"No se pudo extraer texto del PDF {archivo}")
                    
            except Exception as e:
                print(f"Error procesando archivo {i} de {total_archivos}: {str(e)}")
                # Guardar la ruta del PDF incluso cuando hay un error
                subcarpeta = os.path.basename(carpeta)
                pdf_path = f"/uploads/1/{subcarpeta}/{archivo}"
                guardar_dato_no_procesado({
                    'ID': archivo,
                    'PDF_PATH': pdf_path
                }, f"Error al procesar archivo: {str(e)}")
                continue
        
        # Convertir la lista de todos los datos en un DataFrame de pandas
        df_nuevos_datos2 = pd.DataFrame(todos_los_datos_EXCEL)
        
        # Verificar si el DataFrame está vacío
        if df_nuevos_datos2.empty:
            print("No se encontraron datos para procesar.")
            return
        
        # Ordenar los datos por PLACA y FECHA
        df_nuevos_datos2 = df_nuevos_datos2.sort_values(by=['PLACA', 'FECHA'])

        # Convertir los DataFrames a diccionarios para enviarlos en el POST
        datos_para_post_excel = df_nuevos_datos2.to_dict(orient='records')
        
        # Guardar los datos en un archivo Excel
        df_nuevos_datos2.to_excel(ruta_excel, index=False)
        print(f"Excel guardado en: {ruta_excel}")
        
        # Guardar los datos en un archivo JSON
        with open('datos_procesados.json', 'w', encoding='utf-8') as archivo_json:
            json.dump(datos_para_post_excel, archivo_json, ensure_ascii=False, indent=4)
      
        # Enviar los datos al endpoint POST
        total_datos = len(datos_para_post_excel)
        print(f"Iniciando creación de {total_datos} manifiestos...")
        
        for i, datos in enumerate(datos_para_post_excel, 1):
            try:
                # Limpiar los datos antes de enviarlos
                datos['PLACA'] = datos['PLACA'].strip() if datos['PLACA'] else 'DESCONOCIDA'
                datos['ID'] = datos['ID'].strip() if datos['ID'] else 'SIN_ID'
                datos['KOF'] = datos['KOF'].strip() if datos['KOF'] else 'SIN_KOF'
                datos['FECHA'] = datos['FECHA'].strip() if datos['FECHA'] else None
                datos['REMESA'] = datos['REMESA'].strip() if datos['REMESA'] else 'SIN_REMESA'
                datos['CONDUCTOR'] = datos['CONDUCTOR'].strip() if datos['CONDUCTOR'] else 'SIN_CONDUCTOR'
                datos['DESTINO'] = datos['DESTINO'].strip() if datos['DESTINO'] else 'SIN_DESTINO'
                datos['ORIGEN'] = datos['ORIGEN'].strip() if datos['ORIGEN'] else 'SIN_ORIGEN'
                datos['EMPRESA'] = datos['EMPRESA'].strip() if datos['EMPRESA'] else 'SIN_EMPRESA'  
                datos['PDF_PATH'] = datos['PDF_PATH'].strip() if datos['PDF_PATH'] else 'SIN_PDF_PATH'
                datos['NUMERO'] = incrementar_contador(datos['PLACA'])
                
                # Manejar valores NaN
                for key, value in datos.items():
                    if pd.isna(value):
                        if key == 'VALOR_FLETE':
                            datos[key] = 250000
                        elif key == 'FECHA':
                            datos[key] = None
                        else:
                            datos[key] = 'SIN_' + key
                
                # Validar que la fecha no sea nula antes de enviar
                if not datos['FECHA']:
                    raise ValueError("La fecha no puede ser nula")
                
                response = requests.post(url_post, json=datos)
                if response.status_code == 201:
                    print(f"Manifiesto creado: {response.json()}")
                    # Actualizar progreso solo durante la creación de manifiestos (0-100%)
                    progreso = int((i / total_datos) * 100)
                    print(f"Progreso: {progreso}% - Creando manifiesto {i} de {total_datos}")
                else:
                    error = response.json().get('error', 'Error desconocido')
                    print(f"Error al crear manifiesto: {error}")
                    # Guardar el error en datos_no_procesados
                    datos['error'] = str(error)
                    
            except Exception as e:
                print(f"Error al crear manifiesto: {str(e)}")
                
    except Exception as e:
        print(f"Error general en el procesamiento: {str(e)}")
        raise e

def procesar_texto_pdf(texto, nombre_archivo):
    # Aquí va tu lógica de procesamiento del texto
    # Este es un ejemplo básico, ajusta según tus necesidades
    return {
        "archivo": nombre_archivo,
        "fecha_procesamiento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "contenido": texto[:1000]  # Primeros 1000 caracteres como ejemplo
    }

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
        'KOF': KOF[0] if KOF else ' ',
        'REMESA': REMESA[0],
        'EMPRESA': EMPRESA,
        'VALOR_FLETE': valor
    }

    # Agregar el diccionario a la lista de datos
    lista_de_datos.append(datos_excel)

# Diccionario global para almacenar los contadores individuales por placa
contadores_por_placa = {}

def incrementar_contador(placa):
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

def determinar_remolque(placa):
    # Implementa la lógica para determinar el remolque basado en la placa
    return "REMOLQUE123"