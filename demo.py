import sys
import time
import threading
import subprocess
import os
import signal
from pathlib import Path


DEMO_DIR = Path(__file__).parent
CLIENT_FILES = DEMO_DIR / "client_files"
CLIENT_FILES.mkdir(exist_ok=True)


def create_demo_files():
    (CLIENT_FILES / "rapport.txt").write_text(
        "Rapport de sécurité confidentiel\n"
        "================================\n"
        "Sujet : Protocole d'échange de fichiers chiffrés\n\n"
        "Ce document est protégé par chiffrement RSA + AES-256-GCM.\n"
        "Toute interception sera détectée par vérification de signature numérique.\n\n"
        "Auteur : Kader Belkhir\n"
        "Date   : 2025\n"
    )
    (CLIENT_FILES / "data.json").write_text(
        '{"projet": "CryptoExchange", "version": "1.0", "chiffrement": ["RSA-2048", "AES-256-GCM"], "signature": "SHA-256/PSS"}\n'
    )
    print("[DEMO] Fichiers de test créés dans client_files/")


def run_server_subprocess():
    return subprocess.Popen(
        [sys.executable, str(DEMO_DIR / "server.py")],
        cwd=str(DEMO_DIR),
    )


def run_client_demo():
    sys.path.insert(0, str(DEMO_DIR))
    from client import send_files
    time.sleep(1.5)
    files = [str(CLIENT_FILES / "rapport.txt"), str(CLIENT_FILES / "data.json")]
    print("\n" + "═" * 55)
    print("  ENVOI DE FICHIERS CHIFFRÉS")
    print("═" * 55)
    send_files(files)
    print("═" * 55)
    print("  FICHIERS REÇUS DANS server_files/")
    for f in (DEMO_DIR / "server_files").iterdir():
        print(f"  ✓ {f.name} ({f.stat().st_size} octets)")
    print("═" * 55 + "\n")


if __name__ == "__main__":
    create_demo_files()
    srv = run_server_subprocess()
    try:
        run_client_demo()
    finally:
        srv.terminate()
        srv.wait()
        print("[DEMO] Serveur arrêté.")
