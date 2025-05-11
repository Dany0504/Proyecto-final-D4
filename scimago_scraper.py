import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse
import time
import json

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
    search_url = (
        "https://www.scimagojr.com/journalsearch.php"
        f"?clean=0&tip=sid&q={q}"
    )
    
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

def procesar_revistas(titulos):
    resultado = []
    for i, titulo in enumerate(titulos):
        print(f"[{i}] Procesando: {titulo}")
        info = obtener_info_scimago(titulo)
        if info and not es_entrada_vacia(info):
            resultado.append(info)
        time.sleep(1)  # 1  segundos entre cada petición

    salida = "json/salida.json"
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=4, ensure_ascii=False)

# Lista de títulos
titulos_revistas = [
    "2D MATERIALS", "3 BIOTECH", "AAC: AUGMENTATIVE AND ALTERNATIVE COMMUNICATION",
    "AACL BIOFLUX", "AACN ADVANCED CRITICAL CARE", "AANA JOURNAL",
    "AAO JOURNAL", "AAOHN JOURNAL", "AAPS JOURNAL", "AAPS PHARMSCITECH"
]

procesar_revistas(titulos_revistas)
