"""Zrzut strony /docs (Swagger UI) aplikacji FastAPI zbudowanej z listingu książki.

Użycie:
    python fastapi_docs.py <strona.md> <plik-listingu> <python-aplikacji> <metoda> <ścieżka> <wyjście.png>

Przykład (rozdział 15 części „Python Zastosowania”):
    python fastapi_docs.py docs/zastosowania/15-fastapi/pierwsza-aplikacja.md aplikacja.py ^
        C:/venvs/fastapi/Scripts/python.exe get /produkty/{produkt_id} ^
        docs/zastosowania/15-fastapi/img/fastapi-docs.png

Skrypt wyjmuje blok ```python title="<plik-listingu>"``` ze strony do katalogu tymczasowego,
uruchamia go serwerem uvicorn interpretera <python-aplikacji> (środowisko z FastAPI w wersji
z książki) na wolnym porcie pętli zwrotnej, otwiera dokumentację w przeglądarce Microsoft Edge
bez okna (Playwright, kanał „msedge”) z rozwiniętą wskazaną trasą i zapisuje kadr samej listy tras.
Uruchamiać interpreterem środowiska narzędzi z pakietem playwright. W Git Bash wywołanie
poprzedzamy MSYS_NO_PATHCONV=1 — inaczej powłoka zamieni ścieżkę trasy na ścieżkę Windows.
"""
import json
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

SZEROKOSC = 1000


def wyjmij_listing(strona: Path, nazwa: str, katalog: Path) -> None:
    tekst = strona.read_text(encoding="utf-8")
    blok = re.search(rf'^```python title="{re.escape(nazwa)}"\n(.*?)^```', tekst, re.S | re.M)
    if blok is None:
        sys.exit(f"brak bloku {nazwa} na stronie {strona}")
    (katalog / nazwa).write_text(blok.group(1), encoding="utf-8")


def wolny_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def czekaj_na_serwer(adres: str, limit: float = 30.0) -> dict:
    koniec = time.monotonic() + limit
    while time.monotonic() < koniec:
        try:
            with urllib.request.urlopen(f"{adres}/openapi.json", timeout=2) as odpowiedz:
                return json.load(odpowiedz)
        except OSError:
            time.sleep(0.3)
    sys.exit("serwer nie odpowiedział")


def main() -> None:
    strona, plik, python_aplikacji, metoda, sciezka, wyjscie = sys.argv[1:7]
    with tempfile.TemporaryDirectory() as tmp:
        katalog = Path(tmp)
        wyjmij_listing(Path(strona), plik, katalog)
        port = wolny_port()
        serwer = subprocess.Popen(
            [python_aplikacji, "-m", "uvicorn", f"{Path(plik).stem}:app", "--host", "127.0.0.1", "--port", str(port)],
            cwd=katalog, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            adres = f"http://127.0.0.1:{port}"
            opis = czekaj_na_serwer(adres)
            operacja = opis["paths"][sciezka][metoda.lower()]
            znacznik = (operacja.get("tags") or ["default"])[0]
            with sync_playwright() as p:
                przegladarka = p.chromium.launch(channel="msedge")
                karta = przegladarka.new_page(viewport={"width": SZEROKOSC, "height": 900}, color_scheme="light",
                                              locale="pl-PL")
                karta.goto(f"{adres}/docs#/{znacznik}/{operacja['operationId']}")
                karta.wait_for_selector(".opblock.is-open .opblock-body")
                karta.wait_for_timeout(500)
                # kadr: lista tras od nagłówka grupy do końca parametrów rozwiniętej trasy (bez odpowiedzi)
                lista = karta.locator(".opblock-tag-section").first.bounding_box()
                parametry = karta.locator(".opblock.is-open table.parameters").first.bounding_box()
                Path(wyjscie).parent.mkdir(parents=True, exist_ok=True)
                karta.screenshot(path=wyjscie, full_page=True, clip={
                    "x": lista["x"], "y": lista["y"], "width": lista["width"],
                    "height": parametry["y"] + parametry["height"] + 16 - lista["y"],
                })
                przegladarka.close()
        finally:
            serwer.terminate()
            serwer.wait(timeout=10)
    print(f"zapisano {wyjscie}")


if __name__ == "__main__":
    main()
