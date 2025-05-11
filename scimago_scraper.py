import json
import requests
from bs4 import BeautifulSoup
import time
import argparse
import os
from unidecode import unidecode

# Normalizar texto
def normalizar(texto):
    return unidecode(texto.lower().strip())

# obtener datos de la revista desde SCIMAGO
def obtener_info_scimago(titulo):
    query = "+".join(titulo.split())
    url = f"https://www.scimagojr.com/journalsearch.php?q={query}"
    response = requests.get(url)

    if response.status_code != 200:
        return info_no_encontrada(titulo)

    soup = BeautifulSoup(response.text, "html.parser")
    enlaces = soup.find_all("a", href=True, string="View journal")

    if not enlaces:
        return info_no_encontrada(titulo)

    # Verificar coincidencia exacta
    for enlace in enlaces:
        journal_url = "https://www.scimagojr.com/" + enlace['href']
        journal_response = requests.get(journal_url)

        if journal_response.status_code != 200:
            continue

        journal_soup = BeautifulSoup(journal_response.text, "html.parser")
        titulo_encontrado = journal_soup.find("h1")
        if titulo_encontrado and normalizar(titulo_encontrado.text) == normalizar(titulo):
            return extraer_info(journal_soup, titulo, journal_url, True)

    # Si no hay coincidencia exacta, devolver el primero igual
    primer_url = "https://www.scimagojr.com/" + enlaces[0]['href']
    primer_response = requests.get(primer_url)
    if primer_response.status_code == 200:
        primer_soup = BeautifulSoup(primer_response.text, "html.parser")
        return extraer_info(primer_soup, titulo, primer_url, False)

    return info_no_encontrada(titulo)

def extraer_info(soup, titulo, url, match):
    def por_label(label):
        try:
            tag = soup.find("span", string=label)
            if tag:
                return tag.find_next("span").text.strip()
        except:
            pass
        return "No disponible"

    def lista_por_label(label):
        try:
            seccion = soup.find("div", class_="cell", string=label)
            if seccion:
                return [a.text.strip() for a in seccion.find_next_sibling("div").find_all("a")]
        except:
            pass
        return []

    return {
        "titulo": titulo,
        "url": url,
        "h_index": por_label("H index"),
        "publisher": por_label("Publisher"),
        "issn": por_label("ISSN"),
        "subject_areas": lista_por_label("Subject Area and Category"),
        "publication_type": por_label("Type"),
        "homepage": por_label("Homepage"),
        "widget": f"<iframe src='https://www.scimagojr.com/journalsearch.php?q={'+'.join(titulo.split())}' width='100%' height='300'></iframe>",
        "coincidencia_exacta": match
    }

def info_no_encontrada(titulo):
    return {
        "titulo": titulo,
        "url": "No encontrado",
        "h_index": "No disponible",
        "publisher": "No disponible",
        "issn": "No disponible",
        "subject_areas": "No disponible",
        "publication_type": "No disponible",
        "homepage": "No disponible",
        "widget": "No disponible",
        "coincidencia_exacta": False
    }

# Función principal
def ejecutar_scraping():
    parser = argparse.ArgumentParser(description="Scraping de SCIMAGO por rango de revistas")
    parser.add_argument("-a", "--archivo", required=True, help="Archivo JSON con títulos de revistas")
    parser.add_argument("-p", "--primero", type=int, required=True, help="Índice inicial")
    parser.add_argument("-u", "--ultimo", type=int, required=True, help="Índice final")
    parser.add_argument("-o", "--output", required=True, help="Archivo JSON de salida")
    args = parser.parse_args()

    with open(args.archivo, encoding="latin-1") as archivo:
        revistas = json.load(archivo)

    titulos = list(revistas.keys())[args.primero:args.ultimo]
    resultados = []
    ya_procesadas = set()

    if os.path.exists(args.output):
        with open(args.output, "r", encoding="utf-8") as f:
            resultados = json.load(f)
            ya_procesadas = {r["titulo"].lower() for r in resultados}

    for i, titulo in enumerate(titulos, start=args.primero):
        if titulo.lower() in ya_procesadas:
            print(f"[{i}] {titulo} ya procesado. Saltando...")
            continue

        print(f"[{i}] Procesando: {titulo}")
        info = obtener_info_scimago(titulo)
        resultados.append(info)
        time.sleep(1)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

    print(f"✅ {len(resultados)} registros guardados en {args.output}")

# Ejecutar
if __name__ == "__main__":
    ejecutar_scraping()
