import json
import requests
from bs4 import BeautifulSoup
import time
import argparse

# obtener datos de la revista desde SCIMAGO
def obtener_info_scimago(titulo):
    query = "+".join(titulo.split())
    url = f"https://www.scimagojr.com/journalsearch.php?q={query}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"titulo": titulo, "url": "No encontrado", "descripcion": "No disponible", "sjr": "No disponible"}

    soup = BeautifulSoup(response.text, "html.parser")
    enlace = soup.find("a", href=True, string="View journal")

    if enlace is None:
        return {"titulo": titulo, "url": "No encontrado", "descripcion": "No disponible", "sjr": "No disponible"}

    journal_url = "https://www.scimagojr.com/" + enlace['href']
    journal_response = requests.get(journal_url)

    if journal_response.status_code != 200:
        return {"titulo": titulo, "url": journal_url, "descripcion": "No disponible", "sjr": "No disponible"}

    journal_soup = BeautifulSoup(journal_response.text, "html.parser")
    descripcion = journal_soup.select_one(".journaldescription")
    sjr_value = journal_soup.find(text="SJR")
    sjr_score = sjr_value.find_next("div").text.strip() if sjr_value else "No disponible"

    return {
        "titulo": titulo,
        "url": journal_url,
        "descripcion": descripcion.text.strip() if descripcion else "No disponible",
        "sjr": sjr_score
    }

# Función principal
def ejecutar_scraping():
    # Configuración de argumentos
    parser = argparse.ArgumentParser(description="Realiza scraping de SCIMAGO por un rango de revistas")
    parser.add_argument("-a", "--archivo", required=True, help="Archivo JSON con los títulos de revistas")
    parser.add_argument("-p", "--primero", type=int, required=True, help="Índice inicial de las revistas a procesar")
    parser.add_argument("-u", "--ultimo", type=int, required=True, help="Índice final de las revistas a procesar")
    parser.add_argument("-o", "--output", required=True, help="Archivo de salida para los resultados del scraping")

    args = parser.parse_args()

    # Cargar el archivo JSON con los títulos de revistas
    with open(args.archivo, encoding="latin-1") as archivo:
        revistas = json.load(archivo)

    # Filtrar los títulos de revistas según el rango especificado
    titulos_seleccionados = list(revistas.keys())[args.primero:args.ultimo]
    resultados_scraping = []

    # Realizar scraping para cada título seleccionado
    for index, titulo in enumerate(titulos_seleccionados, start=args.primero):
        print(f"Procesando [{index}] {titulo}...")
        datos_revista = obtener_info_scimago(titulo)
        resultados_scraping.append(datos_revista)
        time.sleep(1)  # Esperar 1 segundo entre solicitudes para evitar sobrecargar el servidor

    # Guardar los resultados en un archivo JSON
    with open(args.output, "w", encoding="utf-8") as salida:
        json.dump(resultados_scraping, salida, indent=4, ensure_ascii=False)

    print(f"Se generó el archivo {args.output} con {len(resultados_scraping)} registros.")

# Ejecutar la función principal si el script se ejecuta directamente
if __name__ == "__main__":
    ejecutar_scraping()
