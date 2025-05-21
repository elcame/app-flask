import requests
from bs4 import BeautifulSoup

def obtener_campos_formulario_google(url):
    try:
        # Realizar la solicitud HTTP
        response = requests.get(url)
        response.raise_for_status()  # Verificar si hubo errores en la solicitud

        # Analizar el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar los campos del formulario
        campos = soup.find_all('input', {'required': True})
        for campo in campos:
            print(f"Nombre del campo: {campo.get('name')}, Tipo: {campo.get('type')}")

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el formulario: {e}")

# URL del formulario de Google
url_formulario = "https://docs.google.com/forms/d/e/1FAIpQLSc6O01l8I-nPnJ2zsDtL3WwT14zncSxfiO2C73_P7dEbb-JgQ/viewform"
obtener_campos_formulario_google(url_formulario)
print("Fin del script")