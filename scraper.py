import json
import feedparser
import threading
import pymongo
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "noticias_db"
COLLECTION_NAME = "noticias"

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

collection.create_index([("url", pymongo.ASCENDING)], unique=True)


def obtener_noticias(fuente):
    nombre = fuente["nombre_fuente_rss"]
    url = fuente["url_rss"]
    print(f"📡 Extrayendo noticias de: {nombre}...")

    feed = feedparser.parse(url)
    noticias = []

    for entry in feed.entries:
        noticia = {
            "fuente": nombre,
            "titulo": entry.title,
            "descripcion": entry.summary,
            "url": entry.link,
            "fecha_publicacion": entry.published if "published" in entry else str(datetime.now()),
            "imagen": (
                entry.media_content[0]["url"] if "media_content" in entry else
                entry.enclosures[0]["href"] if "enclosures" in entry and entry.enclosures else
                entry.image.url if hasattr(entry, "image") and hasattr(entry.image, "url") else
                None)
        }

        if not collection.find_one({"url": noticia["url"]}):
            noticias.append(noticia)

    if noticias:
        collection.insert_many(noticias)
        print(f"✅ Guardadas {len(noticias)} noticias de {nombre}")
    else:
        print(f"⚠️ No se encontraron noticias nuevas en {nombre}")


base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, "fuentes_rss.json")

def ejecutar_scraping():
    with open(json_path, "r", encoding="utf-8") as file:
        fuentes = json.load(file)

    num_hilos = os.cpu_count() - 1  
    num_hilos = max(1, num_hilos)  
    
    print(f"💻 Número de cores: {os.cpu_count()}")
    print(f"🔄 Hilos de trabajo creados: {num_hilos}")

    with ThreadPoolExecutor(max_workers=num_hilos) as executor:
        executor.map(obtener_noticias, fuentes)

    print("🚀 Scraping completado.")



if __name__ == "__main__":
    ejecutar_scraping()
