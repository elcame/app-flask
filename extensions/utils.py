import json
import os
from datetime import datetime
import re

def guardar_dato_no_procesado(dato, error=None):
    """
    Guarda los datos no procesados en un archivo JSON.
    
    Args:
        dato (dict): Diccionario con los datos a guardar
        error (str): Mensaje de error que describe por qué no se pudo procesar
    """
    try:
        # Asegurarse que la carpeta existe
        carpeta = 'datos_no_procesados'
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
            
        # Ruta del archivo JSON
        archivo_json = os.path.join(carpeta, 'datos_no_procesados.json')
        
        # Cargar datos existentes o crear lista vacía
        if os.path.exists(archivo_json):
            with open(archivo_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
        else:
            datos = []
            
        # Agregar el nuevo dato
        dato['error'] = error
        datos.append(dato)
        
        # Guardar datos actualizados
        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
            
        return True
    except Exception as e:
        print(f"Error al guardar dato no procesado: {str(e)}")
        return False 