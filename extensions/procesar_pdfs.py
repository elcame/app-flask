import os
import re
import pandas as pd
import fitz  # PyMuPDF
import requests
import json
import openpyxl  # Para manejo de archivos Excel
from datetime import datetime
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
    if fecha:
        fecha[0] = fecha[0].replace('.', '/')
        mes = fecha[0].split('/')[1]
        if mes == '01':
            mes = 'ENERO'
        elif mes == '02':
            mes = 'FEBRERO'
        elif mes == '03':
            mes = 'MARZO'
        elif mes == '04':
            mes = 'ABRIL'
        elif mes == '05':
            mes = 'MAYO'
        elif mes == '06':
            mes = 'JUNIO'
        elif mes == '07':
            mes = 'JULIO'
        elif mes == '08':
            mes = 'AGOSTO'
        elif mes == '09':
            mes = 'SEPTIEMBRE'
        elif mes == '10':
            mes = 'OCTUBRE'
        elif mes == '11':
            mes = 'NOVIEMBRE'
        elif mes == '12':
            mes = 'DICIEMBRE'
    else:
        print('No se encontró la fecha')
        mes = 'MARZO'
     
    if fecha:
        fecha[0] = fecha[0].replace('.', '/').strip()
        try:
            fecha_obj = datetime.strptime(fecha[0], '%d/%m/%Y')
            fecha[0] = fecha_obj.strftime('%Y-%m-%d')  # Convertir a formato 'YYYY-MM-DD'
        except ValueError:
            print(f"Fecha inválida: {fecha[0]}")
            fecha[0] = None
        mes = fecha_obj.strftime('%B').upper() if fecha[0] else 'DESCONOCIDO'
    else:
        print('No se encontró la fecha')
        fecha = [None]
        mes = 'DESCONOCIDO'    
    hora = re.findall(palabraclave2, texto_extraido)
    referencia = re.findall(palabraclave3, texto_extraido)
    conductor = re.findall(palabraclave4, texto_extraido)
    placa = re.findall(palabraclave5, texto_extraido)
    KOF = re.findall(palabraclave6, texto_extraido)
    destino = re.findall(palabraclave8, texto_extraido)
    
    kof = [num for num in KOF]
    KBQ = re.findall(palabraclave7, texto_extraido)
    KBQ = [num for num in KBQ]
    origen = 'BARRANQUILLA'
    destino_final = destino[0] if destino else ' '
    lista_de_datos = []  # Inicializar la lista
    lista_de_EXCEL = []  # Inicializar la lista EXCEL
    jornadaretorno = None

    # Llamar a la función para crear la lista para el excel con el formato del link de envío
    agregar_datos_EXCEL(lista_de_EXCEL, placa, conductor, origen, destino_final, fecha, mes, referencia, kof, KBQ, 'CAMELO ARENAS GUILLERMO ANDRES')
    return lista_de_datos, lista_de_EXCEL

def procesar_pdfs_en_carpeta_para_post(carpeta, url_post='http://localhost:5000/manifiestos'):
    # Inicializar una lista para almacenar todos los datos de todos los PDFs
    todos_los_datos_LINK = []
    todos_los_datos_EXCEL = []
    # Inicializar un conjunto para almacenar todas las combinaciones únicas de PLACA y ID
    combinaciones_unicas = set()
    
    #limpiar el archivo de datos procesados
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
       
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".pdf"):
            ruta_pdf = os.path.join(carpeta, archivo)
            subcarpeta = os.path.basename(carpeta)  # Obtener el nombre de la subcarpeta
            
            # Extraer el texto del PDF
            texto_extraido = pdf_to_text(ruta_pdf)
            
            if texto_extraido:
                # Extraer los datos del texto
                datos_pdf = extraer_datos(texto_extraido)
                lista_datos_link = datos_pdf[0]
                lista_datos_excel = datos_pdf[1]
                
                if lista_datos_excel:
                    # Renombrar los PDFs
                    placa = lista_datos_excel[0]['PLACA'].replace(" ", "")
                    referencia = lista_datos_excel[0]['ID'].replace(" ", "")
                    combinacion = (placa, referencia)
                    if combinacion not in combinaciones_unicas:
                        combinaciones_unicas.add(combinacion)
                        nuevo_nombre = f"global {placa} ID {referencia}.pdf"
                        nuevo_ruta_pdf = os.path.join(carpeta, nuevo_nombre)
                        os.rename(ruta_pdf, nuevo_ruta_pdf)
                        
                        # Agregar los datos del PDF a la lista de todos los datos
                        todos_los_datos_EXCEL.extend(lista_datos_excel)
                    else:
                        print(f"Duplicado encontrado: {ruta_pdf} no será renombrado ni agregado.")
                
                for dato in lista_datos_excel:
                    #a la ruta del pdf se le agrega la ruta de la carpeta y el nombre del pdf
                    print(f"carpeta: {subcarpeta}")
                    dato['PDF_PATH'] = f"/uploads/1/{subcarpeta}/{nuevo_nombre}"  # Ruta relativa para el frontend
                else:
                    print(f"No se encontraron datos en el archivo: {ruta_pdf}")
            else:
                print(f"No se pudo extraer datos del archivo: {ruta_pdf}")
    
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
    for datos in datos_para_post_excel:
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
        
        datos['NUMERO'] = incrementar_contador(datos['PLACA'])
        
        response = requests.post(url_post, json=datos)
        if response.status_code == 201:
            print(f"Manifiesto creado: {response.json()}")
        else:
            print(f"Error al crear manifiesto: {response.text}")

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