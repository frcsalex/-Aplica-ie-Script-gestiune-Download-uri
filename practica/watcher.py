from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import subprocess
from pathlib import Path

# Calea către folderul Downloads
DOWNLOADS = Path("C:/Users/practica/Downloads")  # Dacă e în altă parte, înlocuiește cu Path("C:/Users/NumeleTau/Downloads")

# Scriptul care face organizarea
GESTIUNE_SCRIPT = Path("gestiune_downloaduri.py")  # Pune calea completă dacă e în altă locație

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"[Watcher] Fișier nou: {event.src_path}")
            ruleaza_script()

    def on_modified(self, event):
        if not event.is_directory:
            print(f"[Watcher] Modificare: {event.src_path}")
            ruleaza_script()

def ruleaza_script():
    try:
        subprocess.run(["python", str(GESTIUNE_SCRIPT)], check=True)
        print("[Watcher] Scriptul a fost rulat.")
    except Exception as e:
        print(f"[Eroare] La rularea scriptului: {e}")

if __name__ == "__main__":
    print("[Watcher] Monitorizez folderul Downloads...")
    observer = Observer()
    observer.schedule(MyHandler(), str(DOWNLOADS), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
