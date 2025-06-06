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
        print(f"Intentando guardar dato no procesado en: {archivo_json}")
        
        # Cargar datos existentes o crear lista vacía
        datos = []
        if os.path.exists(archivo_json):
            try:
                with open(archivo_json, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error al leer el archivo JSON existente: {str(e)}")
                # Si hay error al leer, crear un nuevo archivo
                datos = []
        
        # Asegurarse que datos es una lista
        if not isinstance(datos, list):
            print("El archivo JSON no contiene una lista, creando nueva lista")
            datos = []
            
        # Agregar el error a los datos
        dato['error'] = error
        
        # Verificar si el dato ya existe (por ID)
        existe = False
        for i, d in enumerate(datos):
            if d.get('ID') == dato.get('ID'):
                print(f"Actualizando dato existente con ID: {dato.get('ID')}")
                datos[i] = dato
                existe = True
                break
        
        if not existe:
            print(f"Agregando nuevo dato con ID: {dato.get('ID')}")
            datos.append(dato)
        
        with open('datos_no_procesados.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        # Guardar datos actualizados
        try:
            with open(archivo_json, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
            print(f"Dato guardado exitosamente: {dato.get('ID')} - Error: {error}")
            return True
        
        # Guardar datos en datos_no_procesados.json
        except Exception as e:
            print(f"Error al escribir en el archivo JSON: {str(e)}")
            raise
      
    
      
    except Exception as e:
        print(f"Error al guardar dato no procesado: {str(e)}")
        return False 