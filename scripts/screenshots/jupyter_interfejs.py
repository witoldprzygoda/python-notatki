"""Zrzut strony głównej Jupyter Notebook (pasek narzędzi i lista plików) dla podrozdziału notebook.md.

Użycie:
    python jupyter_interfejs.py <python-z-notebook> <wyjście.png>

Przykład (rozdział 1 części „Python Podstawy”):
    python jupyter_interfejs.py C:/venvs/jupyter/Scripts/python.exe docs/01-instalacja/img/jupyter-interfejs.png

Skrypt zakłada w katalogu tymczasowym przykładowy katalog projektu (pliki main.py i requirements.txt),
uruchamia w nim serwer Jupyter Notebook interpreterem <python-z-notebook> (środowisko z pakietem
notebook) na wolnym porcie pętli zwrotnej, bez tokenu i bez otwierania przeglądarki, otwiera stronę
główną w przeglądarce Microsoft Edge bez okna (Playwright, kanał „msedge”, motyw jasny, interfejs
angielski) i zapisuje kadr od nagłówka z menu do ostatniego pliku na liście. Uruchamiać interpreterem
środowiska narzędzi z pakietem playwright. Plik wyjściowy jest obrazem książki, który skrypt odtwarza.
"""
import json
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

PLIKI = {
    "main.py": 'print("pierwszy program")\n',
    "requirements.txt": "numpy\npandas\nmatplotlib\n",
}


def wolny_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def czekaj_na_serwer(adres: str, limit: float = 60.0) -> dict:
    koniec = time.monotonic() + limit
    while time.monotonic() < koniec:
        try:
            with urllib.request.urlopen(f"{adres}/api", timeout=2) as odpowiedz:
                return json.load(odpowiedz)
        except OSError:
            time.sleep(0.5)
    sys.exit("serwer Jupyter nie odpowiedział")


def main() -> None:
    python_notebook, wyjscie = sys.argv[1:3]
    with tempfile.TemporaryDirectory() as tmp:
        projekt = Path(tmp) / "projekt"
        projekt.mkdir()
        for nazwa, tresc in PLIKI.items():
            (projekt / nazwa).write_text(tresc, encoding="utf-8")
        port = wolny_port()
        serwer = subprocess.Popen(
            [python_notebook, "-m", "notebook", "--no-browser", f"--port={port}",
             "--ServerApp.ip=127.0.0.1", "--IdentityProvider.token=", f"--ServerApp.root_dir={projekt}"],
            cwd=projekt, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            adres = f"http://127.0.0.1:{port}"
            czekaj_na_serwer(adres)
            with sync_playwright() as p:
                przegladarka = p.chromium.launch(channel="msedge")
                karta = przegladarka.new_page(viewport={"width": 800, "height": 420}, color_scheme="light",
                                              locale="en-US")
                karta.goto(f"{adres}/tree")
                karta.wait_for_selector(".jp-DirListing-item")
                karta.wait_for_timeout(1500)
                Path(wyjscie).parent.mkdir(parents=True, exist_ok=True)
                # kadr: od nagłówka z logo, menu i kartami „Files / Running” do ostatniego pliku na liście
                ostatni = karta.locator(".jp-DirListing-item").last.bounding_box()
                karta.screenshot(path=wyjscie, clip={"x": 0, "y": 0, "width": 800,
                                                     "height": ostatni["y"] + ostatni["height"] + 14})
                przegladarka.close()
        finally:
            # cały proces serwera razem z ewentualnymi potomnymi (np. jądrami), żeby zwolnić katalog tymczasowy
            subprocess.run(["taskkill", "/PID", str(serwer.pid), "/T", "/F"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            serwer.wait(timeout=10)
    print(f"zapisano {wyjscie}")


if __name__ == "__main__":
    main()
