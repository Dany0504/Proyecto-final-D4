import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse
import time
import json
import argparse

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

def generar_entrada_vacia(titulo, url="No encontrado"):
    return {
        "titulo": titulo,
        "url": url,
        "descripcion": "No disponible",
        "sjr": "No disponible",
        "h_index": "No disponible",
        "subject_area": "No disponible",
        "publisher": "No disponible",
        "issn": "No disponible",
        "publication_type": "No disponible",
        "widget": "No disponible",
        "ultima_visita": datetime.now().isoformat()
    }

def obtener_info_scimago(titulo):
    q = urllib.parse.quote_plus(titulo)
    search_url = f"https://www.scimagojr.com/journalsearch.php?clean=0&tip=sid&q={q}"
    
    try:
        r = requests.get(search_url, headers=HEADERS, timeout=10)
    except:
        return generar_entrada_vacia(titulo)

    if r.status_code != 200:
        return generar_entrada_vacia(titulo)

    soup = BeautifulSoup(r.text, "html.parser")
    enlaces = soup.find_all("a", href=True)
    enlace = next(
        (a for a in enlaces if "clean=0" in a["href"] and "tip=sid" in a["href"]),
        None
    )
    
    if not enlace:
        return generar_entrada_vacia(titulo)

    journal_url = urllib.parse.urljoin("https://www.scimagojr.com/", enlace["href"])
    
    try:
        rj = requests.get(journal_url, headers=HEADERS, timeout=10)
    except:
        return generar_entrada_vacia(titulo, journal_url)

    if rj.status_code != 200:
        return generar_entrada_vacia(titulo, journal_url)

    jsoup = BeautifulSoup(rj.text, "html.parser")

    desc = jsoup.select_one(".journaldescription")
    descripcion = desc.text.strip() if desc else "No disponible"

    # Obtener URL del widget
    widget_url = "No disponible"
    img_tag = jsoup.find("img", src=lambda x: x and "journal_img.php" in x)
    if img_tag:
        widget_url = urllib.parse.urljoin(journal_url, img_tag["src"])

    def extraer(label):
        nodo = jsoup.find(text=label)
        if nodo:
            siguiente_div = nodo.find_next("div")
            if siguiente_div:
                return siguiente_div.text.strip()
        return "No disponible"

    sjr = extraer("SJR")
    h_index = extraer("H-Index")
    subject_area = extraer("Subject Area and Category")
    publisher = extraer("Publisher")
    issn = extraer("ISSN")
    publication_type = extraer("Publication type")

    return {
        "titulo": titulo,
        "url": journal_url,
        "descripcion": descripcion,
        "sjr": sjr,
        "h_index": h_index,
        "subject_area": subject_area,
        "publisher": publisher,
        "issn": issn,
        "publication_type": publication_type,
        "widget": widget_url,
        "ultima_visita": datetime.now().isoformat()
    }

def es_entrada_vacia(info):
    if info["url"] != "No encontrado":
        return False
    campos = ["descripcion", "sjr", "h_index", "subject_area", "publisher", "issn", "publication_type"]
    return all(info[campo] == "No disponible" for campo in campos)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--archivo", required=True, help="Archivo de entrada JSON")
    parser.add_argument("-p", "--posicion_inicio", type=int, default=0)
    parser.add_argument("-u", "--posicion_final", type=int, default=0)
    parser.add_argument("-o", "--output", required=True, help="Archivo de salida JSON")
    args = parser.parse_args()

    with open(args.archivo, "r", encoding="utf-8") as f:
        data = json.load(f)

    titulos_lista = list(data.keys())
    resultados = []

    for i in range(args.posicion_inicio, min(args.posicion_final + 1, len(titulos_lista))):
        titulo = titulos_lista[i]
        print(f"[{i}] Procesando: {titulo}")
        info = obtener_info_scimago(titulo)
        if info and not es_entrada_vacia(info):
            resultados.append(info)
        time.sleep(1)

    # Filtrar campos si quieres solo la URL del widget
    for r in resultados:
        if r["widget"] == "No disponible":
            r.pop("widget", None)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
