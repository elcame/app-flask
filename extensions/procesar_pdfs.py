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
def procesar_pdfs_en_carpeta_para_post(carpeta_pdf):
    resultados = []
    
    # Verificar si la carpeta existe
    if not os.path.exists(carpeta_pdf):
        return {"error": f"La carpeta {carpeta_pdf} no existe"}
    
    # Procesar cada archivo PDF en la carpeta
    for archivo in os.listdir(carpeta_pdf):
        if archivo.lower().endswith('.pdf'):
            ruta_completa = os.path.join(carpeta_pdf, archivo)
            try:
                # Abrir el PDF con PyMuPDF
                doc = fitz.open(ruta_completa)
                texto_completo = ""
                
                # Extraer texto de cada página
                for pagina in doc:
                    texto_completo += pagina.get_text()
                
                # Cerrar el documento
                doc.close()
                
                # Procesar el texto extraído
                resultado = procesar_texto_pdf(texto_completo, archivo)
                resultados.append(resultado)
                
            except Exception as e:
                resultados.append({
                    "archivo": archivo,
                    "error": f"Error al procesar el archivo: {str(e)}"
                })
    
    return resultados

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