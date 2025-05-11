import json
import requests
from bs4 import BeautifulSoup
import time
import argparse
import os

# obtener datos de la revista desde SCIMAGO
def obtener_info_scimago(titulo):
    query = "+".join(titulo.split())
    url = f"https://www.scimagojr.com/journalsearch.php?q={query}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"titulo": titulo, "url": "No encontrado", "h_index": "No disponible"}

    soup = BeautifulSoup(response.text, "html.parser")
    enlace = soup.find("a", href=True, string="View journal")

    if enlace is None:
        return {"titulo": titulo, "url": "No encontrado", "h_index": "No disponible"}

    journal_url = "https://www.scimagojr.com/" + enlace['href']
    journal_response = requests.get(journal_url)

    if journal_response.status_code != 200:
        return {"titulo": titulo, "url": journal_url, "h_index": "No disponible"}

    journal_soup = BeautifulSoup(journal_response.text, "html.parser")

    def extraer_info_por_label(label):
        try:
            elemento = journal_soup.find("span", string=label)
            if elemento:
                return elemento.find_next("span").text.strip()
        except:
            pass
        return "No disponible"

    def extraer_lista_por_label(label):
        try:
            seccion = journal_soup.find("div", class_="cell", string=label)
            if seccion:
                return [item.text.strip() for item in seccion.find_next_sibling("div").find_all("a")]
        except:
            pass
        return []

    return {
        "titulo": titulo,
        "url": journal_url,
        "h_index": extraer_info_por_label("H index"),
        "publisher": extraer_info_por_label("Publisher"),
        "issn": extraer_info_por_label("ISSN"),
        "subject_areas": extraer_lista_por_label("Subject Area and Category"),
        "publication_type": extraer_info_por_label("Type"),
        "homepage": extraer_info_por_label("Homepage"),
        "widget": f"<iframe src='https://www.scimagojr.com/journalsearch.php?q={query}' width='100%' height='300'></iframe>"
    }

# Función principal
def ejecutar_scraping():
    parser = argparse.ArgumentParser(description="Realiza scraping de SCIMAGO por un rango de revistas")
    parser.add_argument("-a", "--archivo", required=True, help="Archivo JSON con los títulos de revistas")
    parser.add_argument("-p", "--primero", type=int, required=True, help="Índice inicial de las revistas a procesar")
    parser.add_argument("-u", "--ultimo", type=int, required=True, help="Índice final de las revistas a procesar")
    parser.add_argument("-o", "--output", required=True, help="Archivo de salida para los resultados del scraping")
    args = parser.parse_args()

    # Cargar el archivo JSON con los títulos de revistas
    with open(args.archivo, encoding="latin-1") as archivo:
        revistas = json.load(archivo)

    titulos_seleccionados = list(revistas.keys())[args.primero:args.ultimo]

    # Verificar si hay resultados anteriores para evitar duplicados
    resultados_scraping = []
    titulos_existentes = set()

    if os.path.exists(args.output):
        with open(args.output, "r", encoding="utf-8") as f:
            resultados_scraping = json.load(f)
            titulos_existentes = {r["titulo"].lower() for r in resultados_scraping}

    # Scraping evitando duplicados
    for index, titulo in enumerate(titulos_seleccionados, start=args.primero):
        if titulo.lower() in titulos_existentes:
            print(f"[{index}] {titulo} ya fue procesado. Saltando...")
            continue

        print(f"Procesando [{index}] {titulo}...")
        datos_revista = obtener_info_scimago(titulo)
        resultados_scraping.append(datos_revista)
        time.sleep(1)  # Esperar 1 segundo entre solicitudes

    # Guardar los resultados en un archivo JSON
    with open(args.output, "w", encoding="utf-8") as salida:
        json.dump(resultados_scraping, salida, indent=4, ensure_ascii=False)

    print(f"Se generó el archivo {args.output} con {len(resultados_scraping)} registros.")

# Ejecutar si se corre directamente
if __name__ == "__main__":
    ejecutar_scraping()
