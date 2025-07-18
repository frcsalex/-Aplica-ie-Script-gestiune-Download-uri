//am pus versiunea care avea erori,am facut cateva schimbari pana sa prezint si acum am facut acele schimbari si aici.
import os
import shutil
import re
import json
import logging
import requests
import mimetypes
import hashlib
from pathlib import Path

Path("logs").mkdir(exist_ok=True)
logger = logging.getLogger("GestiuneDownloads")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler("logs/log.txt", mode="a", encoding="utf-8")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger.handlers = []
logger.addHandler(file_handler)
logger.addHandler(console_handler)

BASE = Path(".")
DOWNLOADS = BASE / "Downloads"
MEDIA = BASE / "Media"
DOCUMENTS = BASE / "Documents"
EXECUTABLES = BASE / "Executables"
for folder in [MEDIA / "Movies", MEDIA / "Series", MEDIA / "Music", DOCUMENTS, EXECUTABLES]:
    folder.mkdir(parents=True, exist_ok=True)

DOCUMENT_EXT = ['.pdf', '.odt', '.doc', '.docx', '.txt']
EXECUTABLE_EXT = ['.exe', '.msi', '.sh']
VIDEO_EXT = ['.mp4', '.mkv', '.avi']
AUDIO_EXT = ['.mp3', '.flac', '.wav']

OMDB_API_KEY = "1bc331e"

def este_duplicat(sursa, destinatie_folder):
    destinatie_fisier = destinatie_folder / sursa.name
    return destinatie_fisier.exists()

def cauta_metadate_omdb(titlu):
    try:
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={titlu}"
        response = requests.get(url)
        logger.debug(f"[OMDb] Caut titlu: {titlu}")
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                logger.info(f"[OMDb] Metadate găsite pentru {titlu}")
                return data
            else:
                logger.warning(f"[OMDb] Nu s-au găsit metadate pentru {titlu}")
        else:
            logger.error(f"[OMDb] Eroare rețea ({response.status_code}) pentru {titlu}")
    except Exception as e:
        logger.error(f"[OMDb] Excepție la căutare: {str(e)}")
    return None

def extrage_an_din_nume(nume):
    match = re.search(r'(19\d{2}|20\d{2})', nume)
    return match.group(0) if match else None

def curata_titlu_film(nume):
    nume = nume.replace('.', ' ').replace('_', ' ').strip()
    return re.sub(r'(19\d{2}|20\d{2})', '', nume).strip()

def tip_fisier(fisier_path):
    import magic
    ext = fisier_path.suffix.lower()
    nume = fisier_path.stem

    if ext in VIDEO_EXT:
        return "film"
    if ext in AUDIO_EXT:
        return "muzica"
    if ext in DOCUMENT_EXT:
        return "document"
    if ext in EXECUTABLE_EXT:
        return "executabil"


    try:
        mime = magic.from_file(str(fisier_path), mime=True)
        if mime and mime.startswith("video"):
            titlu_curat = curata_titlu_film(nume)
            metadate = cauta_metadate_omdb(titlu_curat)
            if metadate and "Year" in metadate:
                if re.search(r"\d{4}–\d{4}", metadate["Year"]):
                    return "serial"
                elif re.match(r"\d{4}$", metadate["Year"]):
                    return "film"
            return "film"
        elif mime and mime.startswith("audio"):
            return "muzica"
        elif "pdf" in mime or "text" in mime or "document" in mime:
            return "document"
        elif "executable" in mime or mime == "application/x-dosexec":
            return "executabil"
    except Exception as e:
        logger.warning(f"[magic] Eroare detectare tip MIME pentru {fisier_path.name}: {e}")

    return "necunoscut"

def muta_film(film_path):
    nume = film_path.stem
    extensie = film_path.suffix
    an = extrage_an_din_nume(nume)
    titlu_curat = curata_titlu_film(nume)
    metadate = None

    if not an:
        metadate = cauta_metadate_omdb(titlu_curat)
        if metadate and "Year" in metadate:
            match_an = re.search(r'\d{4}', metadate["Year"])
            an = match_an.group(0) if match_an else None

    destinatie = MEDIA / "Movies" / (an if an else "Fara_An") / titlu_curat
    destinatie.mkdir(parents=True, exist_ok=True)

    destinatie_fisier = destinatie / f"{nume}{extensie}"
    if destinatie_fisier.exists():
        logger.warning(f"[Film] Fișier duplicat: {film_path.name}. Se șterge sursa.")
        film_path.unlink()
        return

    shutil.move(str(film_path), destinatie_fisier)
    logger.info(f"[Film] Mutat: {film_path.name} -> {destinatie}")

    if metadate:
        with open(destinatie / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadate, f, indent=4, ensure_ascii=False)

def muta_serial(serial_path):
    nume = serial_path.stem
    extensie = serial_path.suffix
    match = re.search(r'[Ss](\d{1,2})[Ee](\d{1,2})', nume)
    sezon = f"Season_{int(match.group(1))}" if match else "Season_Unknown"
    episod = f"Episode_{int(match.group(2))}" if match else "Episode_Unknown"
    titlu_raw = nume[:match.start()] if match else nume
    titlu_curat = re.sub(r'[._]', ' ', titlu_raw).strip().title()

    destinatie = MEDIA / "Series" / titlu_curat / sezon / episod
    destinatie.mkdir(parents=True, exist_ok=True)

    destinatie_fisier = destinatie / f"{nume}{extensie}"
    if destinatie_fisier.exists():
        logger.warning(f"[Serial] Fișier duplicat: {serial_path.name}. Se șterge sursa.")
        serial_path.unlink()
        return

    shutil.move(str(serial_path), destinatie_fisier)
    logger.info(f"[Serial] Mutat: {serial_path.name} -> {destinatie}")

def muta_muzica(piesa_path):
    nume = piesa_path.stem
    extensie = piesa_path.suffix
    artist, melodie = map(str.strip, nume.split('-', 1)) if '-' in nume else ("Necunoscut", nume)
    destinatie = MEDIA / "Music" / artist
    destinatie.mkdir(parents=True, exist_ok=True)

    destinatie_fisier = destinatie / f"{melodie}{extensie}"
    if destinatie_fisier.exists():
        logger.warning(f"[Muzică] Fișier duplicat: {piesa_path.name}. Se șterge sursa.")
        piesa_path.unlink()
        return

    shutil.move(str(piesa_path), destinatie_fisier)
    logger.info(f"[Muzică] Mutata: {piesa_path.name} -> {destinatie}")

def muta_altele(fisier):
    extensie = fisier.suffix.lower()
    destinatie = DOCUMENTS if extensie in DOCUMENT_EXT else EXECUTABLES if extensie in EXECUTABLE_EXT else DOCUMENTS

    destinatie_fisier = destinatie / fisier.name
    if destinatie_fisier.exists():
        logger.warning(f"[Necunoscut] Fișier duplicat: {fisier.name}. Se șterge sursa.")
        fisier.unlink()
        return

    shutil.move(str(fisier), destinatie_fisier)
    logger.info(f"[Alt Tip] Mutat: {fisier.name} -> {destinatie}")

def gestioneaza_toate_directoarele():
    directoare_de_verificat = [DOWNLOADS]  
    for director in directoare_de_verificat:
        for fisier in director.rglob('*'):
            if fisier.is_file():
                try:
                    t = tip_fisier(fisier)
                    if t == "film":
                        muta_film(fisier)
                    elif t == "serial":
                        muta_serial(fisier)
                    elif t == "muzica":
                        muta_muzica(fisier)
                    elif t in ["document", "executabil"]:
                        muta_altele(fisier)
                    else:
                        muta_altele(fisier)
                except Exception as e:
                    logger.error(f"[Eroare] Nu s-a putut procesa {fisier.name}: {str(e)}")


if __name__ == "__main__":
    logger.info("==== Pornire script gestiune_downloaduri.py ====")
    gestioneaza_toate_directoarele()
    logger.info("==== Terminare script ====")
