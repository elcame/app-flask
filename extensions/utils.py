import json
import os
from datetime import datetime
import re

def guardar_dato_no_procesado(datos, error):
    """
    Guarda los datos no procesados en un archivo JSON.
    
    Args:
        datos (dict): Diccionario con los datos a guardar
        error (str): Mensaje de error que describe por qué no se pudo procesar
    """
    try:
        # Crear el directorio si no existe
        if not os.path.exists('datos_no_procesados'):
            os.makedirs('datos_no_procesados')
            
        # Ruta del archivo JSON
        archivo_json = 'datos_no_procesados/datos_no_procesados.json'
        
        # Cargar datos existentes si el archivo existe
        if os.path.exists(archivo_json):
            with open(archivo_json, 'r', encoding='utf-8') as f:
                datos_existentes = json.load(f)
        else:
            datos_existentes = []
            
        # Agregar el nuevo dato con su error
        datos['error'] = error
        datos_existentes.append(datos)
        
        # Guardar todos los datos
        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos_existentes, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        print(f"Error al guardar dato no procesado: {str(e)}") 