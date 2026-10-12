r"""Zrzuty ekranu Visual Studio Code do książki — sterownik działający wewnątrz piaskownicy.

Skrypt uruchamia piaskownica.py (strona hosta) jako zadanie w Piaskownicy systemu Windows;
nie należy go uruchamiać na pulpicie hosta. Zakłada stan po wsb/przygotuj.ps1: Python 3.14
w %LOCALAPPDATA%\Python\pythoncore-3.14-64, kompilacja 3.14t zainstalowana Python Install Managerem,
środowisko C:\projekty\moj-projekt\.venv-t, VS Code w %LOCALAPPDATA%\Programs\Microsoft VS Code,
rozszerzenia w C:\vsc\ext, strony książki zmapowane tylko do odczytu w C:\host\docs.

Użycie (w piaskownicy, interpreterem środowiska narzędzi z Playwright):
    python vsc_zrzuty.py projekty          projekty przykładowe w C:\projekty z listingów książki
    python vsc_zrzuty.py zrzuty [ID ...]    wszystkie zrzuty albo wskazane (klucze słownika SCENARIUSZE:
                                            1 4 8 9 10 11 12 13 14 15 interpreter menedzer)
    python vsc_zrzuty.py proba              zrzut całego okna do C:\zrzuty-vsc\podglad (diagnostyka)
Opcje polecenia zrzuty: --motyw="Default Light Modern" (inny motyw), --wyjscie=<katalog>
(zamiast C:\zrzuty-vsc; obrazy trafiają do <katalog>\zrzuty i <katalog>\warianty).

Każdy zrzut powstaje w osobnej sesji VS Code ze świeżym katalogiem danych użytkownika
(--user-data-dir), wspólnym katalogiem rozszerzeń i tylko tymi rozszerzeniami, które czytelnik
ma zainstalowane w danym miejscu książki (pozostałe: --disable-extension). VS Code jest sterowany
przez protokół Chrome DevTools (--remote-debugging-port, Playwright connect_over_cdp): klawisze,
mysz i odczyt położenia elementów DOM. Rozmiar okna i skalę ustala emulacja metryk urządzenia:
1280×800 punktów CSS (niektóre scenariusze — mniejsze okno) przy skali 1,5; kadry wycina
Page.captureScreenshot. Motyw Light+ („Default Light+”), interfejs angielski, powiększenie 0 —
tak jak dwa pierwsze zrzuty VS Code w książce (vsc-select-interpreter.png,
vsc-environment-manager.png; scenariusze interpreter i menedzer). Ustawienia spoza książki
(USTAWIENIA_BAZOWE) służą wyłącznie wyciszeniu powiadomień i ekranów powitalnych oraz układowi
kadru; ustawienia, które podaje książka, dodaje dopiero scenariusz danego zrzutu.
Gotowe pliki: C:\zrzuty-vsc\zrzuty\<ścieżka względem docs>, warianty: C:\zrzuty-vsc\warianty.
"""
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

KSIAZKA = Path(r"C:\host\docs")
WYMIANA = Path(r"C:\zrzuty-vsc")
ZRZUTY = WYMIANA / "zrzuty"
WARIANTY = WYMIANA / "warianty"
PODGLAD = WYMIANA / "podglad"
LOCAL = Path(os.environ["LOCALAPPDATA"])
PY = LOCAL / "Python" / "pythoncore-3.14-64"
CODE = LOCAL / "Programs" / "Microsoft VS Code" / "Code.exe"
EXT = Path(r"C:\vsc\ext")
DANE = Path(r"C:\vsc\sesje")
PROJEKTY = Path(r"C:\projekty")
SZEROKOSC, WYSOKOSC, SKALA = 1280, 800, 1.5
PORT = 9222
# okno do zrzutów dymków podpowiedzi: maksymalna szerokość dymka to max(0,66 × szerokość edytora, 750),
# więc przy edytorze węższym niż ok. 1136 punktów dymek ma 750 punktów i nie sięga minimapy
SZEROKOSC_DYMKA = 1100

# rozszerzenia w kolejności, w jakiej wprowadza je książka
PYTHON = ["ms-python.python", "ms-python.vscode-pylance", "ms-python.debugpy", "ms-python.vscode-python-envs"]
PYLINT = ["ms-python.pylint"]
CODE_RUNNER = ["formulahendry.code-runner"]
MYPY = ["ms-python.mypy-type-checker"]
JUPYTER = ["ms-toolsai.jupyter", "ms-toolsai.jupyter-keymap", "ms-toolsai.jupyter-renderers",
           "ms-toolsai.vscode-jupyter-cell-tags", "ms-toolsai.vscode-jupyter-slideshow"]
WSZYSTKIE = PYTHON + PYLINT + CODE_RUNNER + MYPY + JUPYTER

USTAWIENIA_BAZOWE = {
    "workbench.colorTheme": "Default Light+",
    "window.zoomLevel": 0,
    "workbench.startupEditor": "none",
    "workbench.welcomePage.walkthroughs.openOnInstall": False,
    "workbench.tips.enabled": False,
    "update.mode": "none",
    "update.showReleaseNotes": False,
    "update.titleBar": False,  # konto piaskownicy jest administratorem: komunikat o aktualizacjach
    "workbench.secondarySideBar.defaultVisibility": "hidden",
    "telemetry.telemetryLevel": "off",
    "extensions.autoUpdate": False,
    "extensions.autoCheckUpdates": False,
    "extensions.ignoreRecommendations": True,
    "chat.disableAIFeatures": True,
    "security.workspace.trust.enabled": False,
    "window.restoreWindows": "none",
    "editor.accessibilitySupport": "off",
    "git.enabled": False,
    # dymek podpowiedzi pod wierszem: przy pliku jednowierszowym nie zasłania karty edytora
    "editor.hover.above": False,
    # kadry robimy przy fokusie poza edytorem: bez ramki bieżącego wiersza
    "editor.renderLineHighlightOnlyWhenFocus": True,
}

# skróty pomocnicze sterownika (polecenia bez domyślnych skrótów albo z niejednoznacznymi)
SKROTY = {
    "notifications.clearAll": "ctrl+shift+alt+f1",
    "workbench.action.closeSidebar": "ctrl+shift+alt+f3",
    "workbench.view.extension.test": "ctrl+shift+alt+f4",
    "testing.runAll": "ctrl+shift+alt+f5",
    "notifications.hideToasts": "ctrl+shift+alt+f7",
    "workbench.action.focusActivityBar": "ctrl+shift+alt+f9",
}


# ---------------------------------------------------------------- listingi książki

def listingi(strona: str, tytul: str) -> list[str]:
    tekst = (KSIAZKA / strona).read_text(encoding="utf-8")
    wzorzec = rf'^```\w+ title="{re.escape(tytul)}"\n(.*?)^```'
    return [m.group(1) for m in re.finditer(wzorzec, tekst, re.S | re.M)]


def listing(strona: str, tytul: str, zawiera: str | None = None) -> str:
    bloki = [b for b in listingi(strona, tytul) if zawiera is None or zawiera in b]
    if not bloki:
        sys.exit(f"brak bloku {tytul!r} na stronie {strona}")
    return bloki[0]


def zapisz(sciezka: Path, tresc: str) -> None:
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    sciezka.write_text(tresc, encoding="utf-8")


def uruchom(*polecenie, cwd=None) -> None:
    print(">", " ".join(str(p) for p in polecenie), flush=True)
    subprocess.run([str(p) for p in polecenie], cwd=cwd, check=True)


def venv(katalog: Path, *pakiety: str, wymagania: Path | None = None) -> Path:
    python = katalog / ".venv" / "Scripts" / "python.exe"
    if not python.exists():
        uruchom(PY / "python.exe", "-m", "venv", ".venv", cwd=katalog)
    if pakiety:
        uruchom(python, "-m", "pip", "install", "--disable-pip-version-check", "-q", *pakiety)
    if wymagania:
        uruchom(python, "-m", "pip", "install", "--disable-pip-version-check", "-q", "-r", wymagania)
    return python


def projekty() -> None:
    # rozdział 1 (konfiguracja.md, venv.md): C:\projekty\moj-projekt z .venv; środowisko .venv-t
    # tworzy wcześniej wsb/przygotuj.ps1 poleceniem py z venv.md
    moj = PROJEKTY / "moj-projekt"
    moj.mkdir(parents=True, exist_ok=True)
    venv(moj)
    # rozdział 16 (testowanie.md): moduł kolo.py, konfiguracja pytest, testy, conftest.py
    kolo = PROJEKTY / "kolo"
    strona = "16-warsztat/testowanie.md"
    for nazwa in ("kolo.py", "pyproject.toml", "test_fixtures.py", "test_kolo.py", "conftest.py"):
        zapisz(kolo / nazwa, listing(strona, nazwa))
    venv(kolo, "pytest")
    uruchom(kolo / ".venv" / "Scripts" / "python.exe", "-m", "pytest", "-q", cwd=kolo)
    shutil.rmtree(kolo / ".pytest_cache", ignore_errors=True)
    for cache in kolo.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
    # część „Python Zastosowania”, rozdział 1 (srodowisko-projektu.md): analiza-pogody
    pogoda = PROJEKTY / "analiza-pogody"
    for podkatalog in ("dane/surowe", "dane/przetworzone", "notatniki", "skrypty", "wyniki"):
        (pogoda / podkatalog).mkdir(parents=True, exist_ok=True)
    strona = "zastosowania/01-jupyter/srodowisko-projektu.md"
    zapisz(pogoda / "requirements.txt", listing(strona, "requirements.txt"))
    zapisz(pogoda / "README.md", "# Analiza pogody\n")
    venv(pogoda, wymagania=pogoda / "requirements.txt")
    for katalog in (moj, kolo, pogoda):
        python = katalog / ".venv" / "Scripts" / "python.exe"
        subprocess.run([str(python), "-m", "pip", "list", "--disable-pip-version-check"])


# ---------------------------------------------------------------- sesja VS Code

class VSCode:
    """Jedna sesja VS Code: świeże dane użytkownika, wybrane rozszerzenia, sterowanie przez CDP."""

    def __init__(self, nazwa: str, folder: Path, pliki=(), ustawienia=None, rozszerzenia=WSZYSTKIE,
                 szerokosc=SZEROKOSC, wysokosc=WYSOKOSC):
        self.nazwa = nazwa
        self.folder = folder
        self.pliki = list(pliki)
        self.ustawienia = {**USTAWIENIA_BAZOWE, **(ustawienia or {})}
        self.rozszerzenia = rozszerzenia
        self.szerokosc, self.wysokosc = szerokosc, wysokosc
        self.dane = DANE / nazwa
        self.proces = None

    def __enter__(self) -> "VSCode":
        shutil.rmtree(self.dane, ignore_errors=True)
        zapisz(self.dane / "User" / "settings.json", json.dumps(self.ustawienia, indent=2))
        zapisz(self.dane / "User" / "keybindings.json",
               json.dumps([{"key": k, "command": c} for c, k in SKROTY.items()], indent=2))
        wylaczone = [r for r in WSZYSTKIE if r not in self.rozszerzenia]
        argumenty = [str(CODE), str(self.folder), *map(str, self.pliki),
                     "--user-data-dir", str(self.dane), "--extensions-dir", str(EXT),
                     f"--remote-debugging-port={PORT}", "--disable-gpu", "--skip-release-notes",
                     "--skip-welcome", "--disable-workspace-trust", "--new-window",
                     "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding"]
        for r in wylaczone:
            argumenty += ["--disable-extension", r]
        env = dict(os.environ)
        env["PATH"] = f"{PY};{PY / 'Scripts'};" + env.get("PATH", "")
        for zmienna in ("PYTHONUTF8", "PYTHONIOENCODING", "VIRTUAL_ENV"):
            env.pop(zmienna, None)
        self.proces = subprocess.Popen(argumenty, env=env)
        self._pw = sync_playwright().start()
        self.przegladarka = self._pw.chromium.connect_over_cdp(self._czekaj_na_cdp())
        self.page = self._czekaj_na_strone()
        self.cdp = self.page.context.new_cdp_session(self.page)
        self.cdp.send("Emulation.setDeviceMetricsOverride", {
            "width": self.szerokosc, "height": self.wysokosc, "deviceScaleFactor": SKALA, "mobile": False})
        # okno piaskownicy nie musi mieć fokusu systemu: kolory jak w aktywnym oknie
        self.cdp.send("Emulation.setFocusEmulationEnabled", {"enabled": True})
        self.page.wait_for_selector(".monaco-workbench .part.statusbar", timeout=60_000)
        self.page.wait_for_timeout(1500)
        return self

    def __exit__(self, *exc) -> None:
        try:
            self._pw.stop()
        finally:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(self.proces.pid)], capture_output=True)
            time.sleep(2)

    @staticmethod
    def _czekaj_na_cdp(limit: float = 60) -> str:
        koniec = time.monotonic() + limit
        while time.monotonic() < koniec:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=2) as odp:
                    json.load(odp)
                    return f"http://127.0.0.1:{PORT}"
            except OSError:
                time.sleep(0.5)
        sys.exit("VS Code nie udostępnił portu CDP")

    def _czekaj_na_strone(self, limit: float = 60) -> Page:
        koniec = time.monotonic() + limit
        while time.monotonic() < koniec:
            for kontekst in self.przegladarka.contexts:
                for strona in kontekst.pages:
                    if "workbench" in strona.url:
                        return strona
            time.sleep(0.5)
        sys.exit("brak okna workbench")

    # ------------------------------------------------ sterowanie

    def klawisz(self, *klawisze: str, pauza: int = 300) -> None:
        for k in klawisze:
            self.page.keyboard.press(k)
            self.page.wait_for_timeout(pauza)

    def polecenie(self, identyfikator: str, pauza: int = 500) -> None:
        nazwy = {"ctrl": "Control", "shift": "Shift", "alt": "Alt"}
        skrot = "+".join(nazwy.get(c, c.upper()) for c in SKROTY[identyfikator].split("+"))
        self.klawisz(skrot, pauza=pauza)

    def paleta(self, tekst: str, pauza: int = 800) -> None:
        self.klawisz("Control+Shift+P")
        self.page.wait_for_selector(".quick-input-widget", state="visible")
        self.page.keyboard.type(tekst, delay=20)
        self.page.wait_for_timeout(pauza)
        self.klawisz("Enter")

    def wyczysc_powiadomienia(self) -> None:
        self.polecenie("notifications.clearAll")
        self.polecenie("notifications.hideToasts")

    def czekaj(self, warunek_js: str, limit: float = 120, opis: str = "") -> object:
        koniec = time.monotonic() + limit
        while time.monotonic() < koniec:
            wynik = self.page.evaluate(warunek_js)
            if wynik:
                return wynik
            self.page.wait_for_timeout(500)
        self.podglad(f"blad-{self.nazwa}")
        sys.exit(f"[{self.nazwa}] nie doczekano się: {opis or warunek_js}")

    def prostokat(self, selektor: str) -> dict:
        r = self.page.evaluate(
            "s => { const e = document.querySelector(s); if (!e) return null;"
            " const r = e.getBoundingClientRect(); return {x: r.x, y: r.y, width: r.width, height: r.height}; }",
            selektor)
        if r is None:
            sys.exit(f"[{self.nazwa}] brak elementu {selektor}")
        return r

    # ------------------------------------------------ zrzuty

    def kadr(self, plik: Path, x: float, y: float, w: float, h: float) -> None:
        x0, y0 = max(0.0, x), max(0.0, y)
        x1, y1 = min(self.szerokosc, x + w), min(self.wysokosc, y + h)
        wynik = self.cdp.send("Page.captureScreenshot", {
            "format": "png", "fromSurface": True,
            "clip": {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0, "scale": 1}})
        plik.parent.mkdir(parents=True, exist_ok=True)
        plik.write_bytes(base64.b64decode(wynik["data"]))
        print(f"[{self.nazwa}] zapisano {plik}", flush=True)

    def kadr_elementu(self, plik: Path, selektor: str, margines: float = 0) -> None:
        r = self.prostokat(selektor)
        self.kadr(plik, r["x"] - margines, r["y"] - margines, r["width"] + 2 * margines, r["height"] + 2 * margines)

    def kadr_listy(self, plik: Path, margines: float = 3, kursor: bool = True) -> None:
        """Kadr widżetu szybkiego wyboru (quick pick) z wąskim marginesem: na czas zrzutu pod widżetem
        leży jednolite tło w kolorze edytora, żeby w marginesie nie było fragmentów okna.
        kursor=False ukrywa na czas zrzutu migający kursor pola tekstowego (obraz nie zależy
        od fazy migania)."""
        self.page.evaluate("""kursor => {
          const w = [...document.querySelectorAll('.quick-input-widget')].find(e => e.offsetParent);
          const d = document.createElement('div'); d.id = 'zrzut-tlo';
          const z = parseInt(getComputedStyle(w).zIndex) || 2550;
          d.style.cssText = `position:fixed;inset:0;background:var(--vscode-editor-background);z-index:${z - 1}`;
          w.parentElement.insertBefore(d, w);
          if (!kursor) { const s = document.createElement('style'); s.id = 'zrzut-kursor';
            s.textContent = '.quick-input-widget input { caret-color: transparent !important; }';
            document.head.appendChild(s); } }""", kursor)
        self.page.wait_for_timeout(200)
        r = self.page.evaluate("""() => { const w = [...document.querySelectorAll('.quick-input-widget')]
          .find(e => e.offsetParent); const r = w.getBoundingClientRect();
          return {x: r.x, y: r.y, width: r.width, height: r.height}; }""")
        self.kadr(plik, r["x"] - margines, r["y"] - margines, r["width"] + 2 * margines, r["height"] + 2 * margines)
        self.page.evaluate("() => { document.getElementById('zrzut-tlo')?.remove();"
                           " document.getElementById('zrzut-kursor')?.remove(); }")

    def podglad(self, nazwa: str) -> None:
        self.kadr(PODGLAD / f"{nazwa}.png", 0, 0, self.szerokosc, self.wysokosc)


# ---------------------------------------------------------------- scenariusze

def proba() -> None:
    folder = PROJEKTY / "moj-projekt"
    zapisz(folder / "main.py", 'print("pierwszy program")\n')
    with VSCode("proba", folder, [folder / "main.py"], rozszerzenia=PYTHON) as vsc:
        vsc.page.wait_for_timeout(8000)
        vsc.podglad("proba-okno")
        print(vsc.page.evaluate("[window.innerWidth, window.innerHeight, window.devicePixelRatio]"))
        print(vsc.page.evaluate("document.querySelector('.part.statusbar').innerText"))


SCENARIUSZE: dict[str, callable] = {}


def scenariusz(identyfikator: str):
    def rejestruj(funkcja):
        SCENARIUSZE[identyfikator] = funkcja
        return funkcja
    return rejestruj


def interpreter(folder: Path) -> dict:
    return {"python.defaultInterpreterPath": str(folder / ".venv" / "Scripts" / "python.exe")}


JS_LINIA = """(n, zMarginesem) => {
  const linie = [...document.querySelectorAll('.editor-instance .view-line')];
  const wys = linie.length ? linie[0].getBoundingClientRect().height : 0;
  const top0 = Math.min(...linie.map(l => parseFloat(l.style.top)));
  const l = linie.find(l => Math.round((parseFloat(l.style.top) - top0) / wys) === n - 1);
  if (!l) return null;
  const r = l.getBoundingClientRect();
  const tekst = l.querySelector('span');
  const t = tekst.getBoundingClientRect();
  const ed = document.querySelector('.editor-instance .monaco-editor').getBoundingClientRect();
  let x = ed.x;
  if (!zMarginesem) {
    // lewa krawędź cyfr numeru wiersza (bez pustego marginesu na pułapki)
    const numery = [...document.querySelectorAll('.editor-instance .margin-view-overlays .line-numbers')];
    const zakres = document.createRange();
    const lewe = numery.filter(e => e.firstChild).map(e => { zakres.selectNodeContents(e); return zakres.getBoundingClientRect().x; });
    if (lewe.length) x = Math.min(...lewe);
  }
  return {x: x, y: r.y, width: t.right - x, height: r.height};
}"""


def linia(vsc: VSCode, n: int, z_marginesem: bool = False) -> dict:
    """Prostokąt wiersza n do końca tekstu: od cyfr numeru wiersza albo od lewej krawędzi edytora
    (z marginesem na pułapki, z_marginesem=True)."""
    return vsc.czekaj(f"({JS_LINIA})({n}, {json.dumps(z_marginesem)})", opis=f"wiersz {n}")


JS_TOKEN = """t => {
  for (const s of document.querySelectorAll('.editor-instance .view-line span span')) {
    if (s.textContent.replace(/ /g, ' ').includes(t)) {
      const r = s.getBoundingClientRect();
      return {x: r.x, y: r.y, width: r.width, height: r.height};
    }
  }
  return null;
}"""


def token(vsc: VSCode, tekst: str) -> dict:
    return vsc.czekaj(f"({JS_TOKEN})({json.dumps(tekst)})", opis=f"token {tekst}")


def najedz(vsc: VSCode, tekst: str, oczekiwane: str, limit: float = 180) -> dict:
    """Ustawia mysz nad tokenem i czeka, aż dymek podpowiedzi zawiera tekst `oczekiwane`."""
    koniec = time.monotonic() + limit
    while time.monotonic() < koniec:
        t = token(vsc, tekst)
        vsc.page.mouse.move(5, vsc.wysokosc - 5)
        vsc.page.wait_for_timeout(400)
        vsc.page.mouse.move(t["x"] + t["width"] / 2, t["y"] + t["height"] / 2, steps=4)
        try:
            vsc.page.wait_for_selector(".monaco-hover:not(.hidden) .hover-contents, .monaco-hover-content",
                                       state="visible", timeout=4000)
        except Exception:
            continue
        vsc.page.wait_for_timeout(700)
        dymek = vsc.page.evaluate(
            "() => { const h = [...document.querySelectorAll('.monaco-hover')].find(e => e.offsetParent);"
            " if (!h) return null; const r = h.getBoundingClientRect();"
            " return {x: r.x, y: r.y, width: r.width, height: r.height, tekst: h.innerText}; }")
        if dymek and oczekiwane in dymek["tekst"]:
            return dymek
        vsc.page.wait_for_timeout(2000)
    vsc.podglad(f"blad-{vsc.nazwa}")
    sys.exit(f"[{vsc.nazwa}] dymek bez tekstu {oczekiwane!r}")


def suma(*prostokaty: dict, margines: float = 8, pion: float | None = None,
         gora: float | None = None) -> tuple[float, float, float, float]:
    """Prostokąt obejmujący wszystkie podane, z marginesem (`pion` — osobny margines pionowy);
    `gora` — najwyższa dopuszczalna krawędź."""
    pion = margines if pion is None else pion
    x0 = min(p["x"] for p in prostokaty) - margines
    y0 = min(p["y"] for p in prostokaty) - pion
    if gora is not None:
        y0 = max(y0, gora)
    x1 = max(p["x"] + p["width"] for p in prostokaty) + margines
    y1 = max(p["y"] + p["height"] for p in prostokaty) + pion
    return x0, y0, x1 - x0, y1 - y0


def gora_edytora(vsc: VSCode) -> float:
    """Górna krawędź obszaru tekstu edytora (pod ścieżką nawigacyjną)."""
    return vsc.prostokat(".editor-instance .monaco-editor")["y"]


def koniec_wiersza(plik: Path, n: int) -> str:
    """Argument --goto: kursor za ostatnim znakiem wiersza n (bez podświetlenia wystąpień słowa)."""
    return f"{plik}:{n}:{len(plik.read_text(encoding='utf-8').splitlines()[n - 1]) + 1}"


def poszerz_pasek_boczny(vsc: VSCode, o: float) -> None:
    """Przeciąga krawędź paska bocznego w prawo o `o` punktów (pełne etykiety w widoku)."""
    pasek = vsc.prostokat(".part.sidebar")
    x, y = pasek["x"] + pasek["width"] + 1, pasek["y"] + pasek["height"] / 2
    vsc.page.mouse.move(x, y)
    vsc.page.wait_for_timeout(300)
    vsc.page.mouse.down()
    vsc.page.mouse.move(x + o / 2, y, steps=5)
    vsc.page.mouse.move(x + o, y, steps=5)
    vsc.page.mouse.up()
    vsc.page.wait_for_timeout(500)
    vsc.page.mouse.move(vsc.szerokosc / 2, vsc.wysokosc - 5)


def odfokusuj_edytor(vsc: VSCode) -> None:
    """Przenosi fokus na pasek aktywności, żeby w kadrze nie było kursora tekstowego."""
    vsc.polecenie("workbench.action.focusActivityBar")
    vsc.page.mouse.move(vsc.szerokosc / 2, vsc.wysokosc - 5)


# ------------------------------------------------ rozdział 1: pylint i Code Runner

@scenariusz("1")
def pylint_blad() -> None:
    folder = PROJEKTY / "moj-projekt"
    plik = folder / "main.py"
    zapisz(plik, listing("01-instalacja/konfiguracja.md", "main.py", 'print "'))
    # wersja główna: bez Pylance (ustawienie z sekcji „Usuwanie Pylance”) — z Pylance dymek nad
    # słowem print zawiera także całą dokumentację funkcji print(); ten stan zapisujemy jako wariant
    warianty = [("", {"python.languageServer": "None"}), ("-z-pylance", {})]
    for koncowka, dodatkowe in warianty:
        with VSCode(f"1-pylint{koncowka}", folder, ["--goto", koniec_wiersza(plik, 1)],
                    {**interpreter(folder), **dodatkowe},
                    rozszerzenia=PYTHON + PYLINT, szerokosc=SZEROKOSC_DYMKA) as vsc:
            vsc.polecenie("workbench.action.closeSidebar")
            vsc.czekaj("document.querySelector('.editor-instance .squiggly-error')", opis="podkreślenie")
            odfokusuj_edytor(vsc)
            vsc.wyczysc_powiadomienia()
            dymek = najedz(vsc, "print", "Pylint")
            print(f"[{vsc.nazwa}] dymek: {dymek['tekst']!r}")
            cel = (ZRZUTY / "01-instalacja/img/vsc-pylint-blad.png" if not koncowka
                   else WARIANTY / f"vsc-pylint-blad{koncowka}.png")
            vsc.kadr(cel, *suma(linia(vsc, 1), dymek, gora=gora_edytora(vsc)))
            vsc.podglad(vsc.nazwa)


@scenariusz("4")
def code_runner() -> None:
    folder = PROJEKTY / "moj-projekt"
    plik = folder / "main.py"
    zapisz(plik, listing("01-instalacja/konfiguracja.md", "main.py", "pierwszy program"))
    warianty = [("", {}), ("-terminal", {"code-runner.runInTerminal": True})]
    for koncowka, dodatkowe in warianty:
        with VSCode(f"4-code-runner{koncowka}", folder, [plik], {**interpreter(folder), **dodatkowe},
                    rozszerzenia=PYTHON + PYLINT + CODE_RUNNER, szerokosc=960, wysokosc=640) as vsc:
            vsc.page.wait_for_timeout(5000)
            vsc.wyczysc_powiadomienia()
            vsc.page.click(".editor-instance .view-lines")
            vsc.klawisz("Control+Alt+N")
            if koncowka:
                # pierwsze uruchomienie tworzy terminal „Code”, do którego rozszerzenie Python
                # dopisuje potem aktywację .venv; zrzut z drugiego uruchomienia w wyczyszczonym terminalu
                vsc.page.wait_for_timeout(6000)
                vsc.page.click(".part.panel .terminal-wrapper")
                vsc.page.keyboard.type("cls", delay=40)
                vsc.klawisz("Enter", pauza=2500)
                vsc.page.click(".editor-instance .view-lines")
                vsc.klawisz("Control+Alt+N")
                vsc.page.wait_for_timeout(4000)
            else:
                vsc.czekaj("document.querySelector('.part.panel')?.innerText.includes('[Done]')",
                           opis="wynik w panelu Output")
            vsc.page.wait_for_timeout(1500)
            odfokusuj_edytor(vsc)
            vsc.wyczysc_powiadomienia()
            vsc.page.wait_for_timeout(500)
            cel = (ZRZUTY / "01-instalacja/img/vsc-code-runner.png" if not koncowka
                   else WARIANTY / f"vsc-code-runner{koncowka}.png")
            panel = vsc.prostokat(".part.panel")
            # dół kadru: ostatni niepusty wiersz wyniku (Output: wiersze edytora, terminal: kursor)
            dol = vsc.page.evaluate("""() => {
              const p = document.querySelector('.part.panel');
              const wiersze = [...p.querySelectorAll('.view-line')].filter(l => l.innerText.trim());
              if (wiersze.length) return Math.max(...wiersze.map(l => l.getBoundingClientRect().bottom));
              const k = p.querySelector('.xterm-helper-textarea, .xterm-cursor');
              return k ? k.getBoundingClientRect().bottom + 4 : null; }""")
            wysokosc = (dol + 14 - panel["y"]) if dol else panel["height"]
            vsc.kadr(cel, panel["x"], panel["y"], panel["width"], min(wysokosc, panel["height"]))
            vsc.podglad(vsc.nazwa)


# ------------------------------------------------ rozdział 1: wybór interpretera i menedżera środowiska

JS_POLE = "document.querySelector('.quick-input-widget input')?.placeholder || ''"

# pozycje listy Python: Select Interpreter w projekcie moj-projekt: środowiska .venv i .venv-t
# z venv.md oraz instalacje 3.14 i 3.14t (wsb/przygotuj.ps1); ścieżki są wspólne dla obu trybów
INTERPRETERY = [r".\.venv\Scripts\python.exe", r".\.venv-t\Scripts\python.exe",
                r"pythoncore-3.14-64\python.exe", r"pythoncore-3.14t-64\python3.14t.exe"]


def lista_stabilna(vsc: VSCode, limit: float = 30) -> str:
    """Czeka, aż wiersze widżetu szybkiego wyboru przestaną się zmieniać; zwraca ich tekst."""
    poprzedni, koniec = None, time.monotonic() + limit
    while time.monotonic() < koniec:
        vsc.page.wait_for_timeout(1500)
        tekst = opis_quick_pick(vsc)
        if tekst == poprzedni:
            return tekst
        poprzedni = tekst
    return poprzedni or ""


@scenariusz("interpreter")
def wybor_interpretera() -> None:
    """Lista Python: Select Interpreter i następny krok po pozycji Create Virtual Environment...
    (konfiguracja.md). Rozszerzenie Python działa w dwóch trybach: domyślnym
    (python.useEnvironmentsExtension = false, listy samego rozszerzenia Python) i w trybie
    rozszerzenia Python Environments, który Microsoft włącza użytkownikom stopniowo przez
    eksperymenty (w piaskownicy z wyłączoną telemetrią eksperymentów nie ma, więc tryb włącza
    ustawienie). Po Create Virtual Environment... tryb domyślny pyta o typ środowiska (Venv, Conda),
    a tryb Python Environments — o menedżera środowiska. Książka pokazuje listę interpreterów
    z trybu domyślnego i listę menedżerów z trybu Python Environments; drugi obraz każdego trybu
    trafia do wariantów. Bez python.defaultInterpreterPath: interpreter projektu wybiera samo
    rozszerzenie, jak u czytelnika. Drugą listę zamyka klawisz Esc — środowisko nie powstaje."""
    folder = PROJEKTY / "moj-projekt"
    plik = folder / "main.py"
    zapisz(plik, listing("01-instalacja/konfiguracja.md", "main.py", "pierwszy program"))
    tryby = [  # nazwa sesji, ustawienia, kadr listy interpreterów, kadr następnej listy
        ("interpreter", {}, ZRZUTY / "01-instalacja/img/vsc-select-interpreter.png",
         WARIANTY / "vsc-environment-type.png"),
        ("interpreter-python-envs", {"python.useEnvironmentsExtension": True},
         WARIANTY / "vsc-select-interpreter-python-envs.png",
         ZRZUTY / "01-instalacja/img/vsc-environment-manager.png"),
    ]
    for nazwa, ustawienia, cel_interpretery, cel_nastepna in tryby:
        with VSCode(nazwa, folder, [plik], ustawienia, rozszerzenia=PYTHON + PYLINT + CODE_RUNNER) as vsc:
            vsc.page.wait_for_timeout(8000)
            vsc.wyczysc_powiadomienia()
            vsc.paleta("Python: Select Interpreter", pauza=1500)
            vsc.czekaj(f"(w => {{ const t = [...document.querySelectorAll('.quick-input-widget .monaco-list-row')]"
                       f".map(r => r.innerText).join('\\n'); return w.every(s => t.includes(s)); }})"
                       f"({json.dumps(INTERPRETERY)})", limit=180, opis="pełna lista interpreterów")
            vsc.page.mouse.move(vsc.szerokosc / 2, vsc.wysokosc - 5)
            lista = lista_stabilna(vsc)
            pole = vsc.page.evaluate(JS_POLE)
            print(f"[{vsc.nazwa}] pole: {pole!r}")
            print(f"[{vsc.nazwa}] lista interpreterów: {lista!r}", flush=True)
            vsc.kadr_listy(cel_interpretery, kursor=False)
            vsc.podglad(vsc.nazwa)
            wybierz_z_listy(vsc, "Create Virtual Environment")
            vsc.czekaj(f"(p => {{ const w = [...document.querySelectorAll('.quick-input-widget')]"
                       f".find(e => e.offsetParent); return !!w && ({JS_POLE}) !== p"
                       f" && [...w.querySelectorAll('.monaco-list-row')]"
                       f".some(r => /\\bvenv\\b/i.test(r.innerText)); }})({json.dumps(pole)})",
                       limit=60, opis="lista z pozycją venv po Create Virtual Environment")
            vsc.page.mouse.move(vsc.szerokosc / 2, vsc.wysokosc - 5)
            lista = lista_stabilna(vsc)
            print(f"[{vsc.nazwa}] pole: {vsc.page.evaluate(JS_POLE)!r}")
            print(f"[{vsc.nazwa}] następna lista: {lista!r}", flush=True)
            vsc.kadr_listy(cel_nastepna, kursor=False)
            vsc.podglad(vsc.nazwa + "-nastepna")
            vsc.klawisz("Escape")


SCENARIUSZE["menedzer"] = wybor_interpretera


# ------------------------------------------------ rozdział 3: Pylance i mypy

TYPY_INLAY = '''ceny = [19.99, 5.49]
srednia = sum(ceny) / len(ceny)
wynik = ceny[0] if ceny else None


def podwojona(cena: float):
    return 2 * cena
'''

TYPY_MYPY = 'wiek: int = "25"\n'


@scenariusz("8")
def pylance_inlay() -> None:
    folder = PROJEKTY / "moj-projekt"
    plik = folder / "typy.py"
    zapisz(plik, TYPY_INLAY)
    ustawienia = {**interpreter(folder), "pylint.args": ["--errors-only"],
                  "python.analysis.inlayHints.variableTypes": True,
                  "python.analysis.inlayHints.functionReturnTypes": True}
    ostatni = len(TYPY_INLAY.splitlines()) + 1  # pusty wiersz za ostatnim: kursor bez podświetlenia słowa
    with VSCode("8-inlay", folder, ["--goto", f"{plik}:{ostatni}:1"], ustawienia,
                rozszerzenia=PYTHON + PYLINT + CODE_RUNNER) as vsc:
        vsc.czekaj("document.querySelectorAll('.editor-instance [class*=\"dyn-rule\"], "
                   ".editor-instance .inlay-hint, .editor-instance [class*=\"inlay\"]').length > 0",
                   limit=180, opis="inlay hints")
        vsc.page.wait_for_timeout(3000)
        odfokusuj_edytor(vsc)
        vsc.wyczysc_powiadomienia()
        vsc.page.wait_for_timeout(500)
        prostokaty = [linia(vsc, n) for n in range(1, TYPY_INLAY.count("\n") + 1)]
        print(vsc.page.evaluate("[...document.querySelectorAll('.editor-instance .view-line')]"
                                ".map(l => l.innerText)"))
        x, y, w, h = suma(*prostokaty, pion=3, gora=gora_edytora(vsc))
        vsc.kadr(ZRZUTY / "03-nazwy-typy/img/vsc-pylance-inlay-hint.png", x, y, w + 40, h)
        vsc.podglad(vsc.nazwa)


@scenariusz("9")
def mypy_ostrzezenie() -> None:
    folder = PROJEKTY / "moj-projekt"
    plik = folder / "typy.py"
    zapisz(plik, TYPY_MYPY)
    ustawienia = {**interpreter(folder), "pylint.args": ["--errors-only"]}
    with VSCode("9-mypy", folder, ["--goto", koniec_wiersza(plik, 1)], ustawienia,
                rozszerzenia=PYTHON + PYLINT + CODE_RUNNER + MYPY, szerokosc=SZEROKOSC_DYMKA) as vsc:
        vsc.polecenie("workbench.action.closeSidebar")
        vsc.czekaj("document.querySelector('.editor-instance .squiggly-error, .editor-instance .squiggly-warning')",
                   limit=180, opis="podkreślenie mypy")
        odfokusuj_edytor(vsc)
        vsc.wyczysc_powiadomienia()
        dymek = najedz(vsc, '"25"', "Mypy")
        print(f"[{vsc.nazwa}] dymek: {dymek['tekst']!r}")
        vsc.kadr(ZRZUTY / "03-nazwy-typy/img/vsc-mypy-ostrzezenie.png",
                 *suma(linia(vsc, 1), dymek, gora=gora_edytora(vsc)))
        vsc.podglad(vsc.nazwa)


# ------------------------------------------------ rozdział 8: debugger

def opis_quick_pick(vsc: VSCode) -> str:
    return vsc.page.evaluate("document.querySelector('.quick-input-widget')?.innerText || ''")


def wybierz_z_listy(vsc: VSCode, etykieta: str, limit: float = 60) -> None:
    vsc.czekaj("(t => [...document.querySelectorAll('.quick-input-widget .monaco-list-row')]"
               f".some(r => r.innerText.includes(t)))({json.dumps(etykieta)})", limit=limit,
               opis=f"pozycja {etykieta}")
    print(f"[{vsc.nazwa}] lista: {opis_quick_pick(vsc)!r}", flush=True)
    vsc.page.keyboard.type(etykieta, delay=20)
    vsc.page.wait_for_timeout(600)
    vsc.klawisz("Enter", pauza=800)


@scenariusz("10")
def debugger() -> None:
    folder = PROJEKTY / "moj-projekt"
    plik = folder / "debug-silnia.py"
    zrodlo = listing("08-wyjatki/diagnostyka.md", "debug-silnia.py")
    zapisz(plik, zrodlo)
    shutil.rmtree(folder / ".vscode", ignore_errors=True)
    nr = zrodlo.splitlines().index("        return 1") + 1
    ustawienia = {**interpreter(folder), "pylint.args": ["--errors-only"]}
    with VSCode("10-debugger", folder, ["--goto", f"{plik}:{nr}:9"], ustawienia,
                rozszerzenia=PYTHON + PYLINT + CODE_RUNNER + MYPY, wysokosc=680) as vsc:
        vsc.page.wait_for_timeout(6000)
        vsc.wyczysc_powiadomienia()
        vsc.klawisz("Control+1")  # fokus w edytorze, kursor w wierszu return 1 (--goto)
        vsc.klawisz("F9")
        vsc.czekaj("document.querySelector('.editor-instance .codicon-debug-breakpoint')", opis="pułapka")
        vsc.klawisz("F5", pauza=1500)
        vsc.page.wait_for_selector(".quick-input-widget", state="visible", timeout=30_000)
        vsc.kadr_listy(WARIANTY / "f5-krok1-select-debugger.png")
        tekst = opis_quick_pick(vsc)
        if "Python File" not in tekst:
            wybierz_z_listy(vsc, "Python Debugger")
            vsc.page.wait_for_timeout(1000)
            vsc.kadr_listy(WARIANTY / "f5-krok2-debug-configuration.png")
        wybierz_z_listy(vsc, "Python File")
        vsc.czekaj("document.querySelector('.debug-toolbar') && "
                   "document.querySelector('.editor-instance .debug-top-stack-frame-line')",
                   limit=120, opis="zatrzymanie na pułapce")
        vsc.czekaj("(document.querySelector('.debug-call-stack')||{}).innerText?.includes('<module>')",
                   opis="stos wywołań")
        vsc.page.wait_for_timeout(1500)
        # zakres Locals bywa zwinięty, gdy widok Run and Debug otwiera się razem z zatrzymaniem;
        # rozwijamy go, a zaznaczenie wiersza zdejmujemy klawiszem Esc
        js_n = r"/\bn\s*=\s*1\b/.test(document.querySelector('.debug-variables').innerText)"
        if not vsc.page.evaluate(js_n):
            vsc.page.locator(".debug-variables .monaco-list-row", has_text="Locals").first.click()
            vsc.czekaj(js_n, opis="n = 1 w panelu Variables")
            vsc.klawisz("Escape")
        odfokusuj_edytor(vsc)
        vsc.wyczysc_powiadomienia()
        vsc.page.wait_for_timeout(1000)
        # pasek debugowania przed poszerzeniem paska bocznego: wtedy nie nachodzi na kartę edytora
        vsc.kadr_elementu(ZRZUTY / "08-wyjatki/img/vsc-debugger-pasek.png", ".debug-toolbar", 4)
        poszerz_pasek_boczny(vsc, 60)
        odfokusuj_edytor(vsc)
        vsc.page.wait_for_timeout(800)
        print(vsc.page.evaluate("document.querySelector('.part.sidebar').innerText"))
        prostokaty = [linia(vsc, n, z_marginesem=True) for n in range(1, zrodlo.count("\n") + 1)]
        x, y, w, h = suma(*prostokaty, margines=0, pion=3, gora=gora_edytora(vsc))
        vsc.kadr(ZRZUTY / "08-wyjatki/img/vsc-debugger-pulapka.png", x, y, w + 40, h)
        vsc.kadr_elementu(ZRZUTY / "08-wyjatki/img/vsc-debugger-stos-i-zmienne.png", ".part.sidebar")
        vsc.podglad(vsc.nazwa)
        vsc.klawisz("Shift+F5", pauza=1500)


SCENARIUSZE["11"] = SCENARIUSZE["12"] = debugger


# ------------------------------------------------ rozdział 16: widok Testing

@scenariusz("13")
def testing() -> None:
    folder = PROJEKTY / "kolo"
    shutil.rmtree(folder / ".vscode", ignore_errors=True)
    shutil.rmtree(folder / ".pytest_cache", ignore_errors=True)
    for cache in folder.glob("**/__pycache__"):
        if ".venv" not in cache.parts:
            shutil.rmtree(cache, ignore_errors=True)
    ustawienia = {**interpreter(folder), "pylint.args": ["--errors-only"]}
    with VSCode("13-testing", folder, [], ustawienia,
                rozszerzenia=PYTHON + PYLINT + CODE_RUNNER + MYPY) as vsc:
        vsc.page.wait_for_timeout(8000)
        vsc.wyczysc_powiadomienia()
        vsc.paleta("Python: Configure Tests", pauza=1200)
        wybierz_z_listy(vsc, "pytest")
        vsc.page.wait_for_timeout(1000)
        vsc.kadr_listy(WARIANTY / "configure-tests-katalog.png")
        wybierz_z_listy(vsc, "Root directory")
        vsc.page.wait_for_timeout(2000)
        print(f"[{vsc.nazwa}] settings.json:",
              (folder / ".vscode" / "settings.json").read_text(encoding="utf-8")
              if (folder / ".vscode" / "settings.json").exists() else "brak")
        vsc.polecenie("workbench.view.extension.test")
        vsc.czekaj("[...document.querySelectorAll('.part.sidebar .monaco-list-row')]"
                   ".some(r => r.innerText.trim() === 'kolo')", limit=180, opis="wykryte testy")
        vsc.polecenie("testing.runAll")
        vsc.czekaj("document.querySelectorAll('.part.sidebar .codicon-testing-passed-icon').length >= 1"
                   " && !document.querySelector('.part.sidebar').innerText.includes('No test results yet')",
                   limit=180, opis="wyniki testów")
        vsc.page.wait_for_timeout(2000)
        # rozwinięcie wszystkich węzłów drzewa (klik w strzałkę nie zmienia zaznaczenia)
        for _ in range(8):
            zwiniete = vsc.page.query_selector_all(
                ".part.sidebar .monaco-list-row[aria-expanded='false'] .monaco-tl-twistie")
            if not zwiniete:
                break
            zwiniete[0].click()
            vsc.page.wait_for_timeout(500)
        vsc.klawisz("Escape")
        poszerz_pasek_boczny(vsc, 60)
        odfokusuj_edytor(vsc)
        vsc.wyczysc_powiadomienia()
        vsc.page.wait_for_timeout(1000)
        print(vsc.page.evaluate("document.querySelector('.part.sidebar').innerText"))
        pasek = vsc.prostokat(".part.sidebar")
        dol = vsc.page.evaluate("Math.max(...[...document.querySelectorAll('.part.sidebar .monaco-list-row')]"
                                ".map(r => r.getBoundingClientRect().bottom))")
        vsc.kadr(ZRZUTY / "16-warsztat/img/vsc-testing-panel.png",
                 pasek["x"], pasek["y"], pasek["width"], min(dol + 10, pasek["y"] + pasek["height"]) - pasek["y"])
        vsc.podglad(vsc.nazwa)


# ------------------------------------------------ „Python Zastosowania”, rozdział 1: Jupyter

@scenariusz("14")
def jupyter() -> None:
    folder = PROJEKTY / "analiza-pogody"
    with VSCode("14-jupyter", folder, [], interpreter(folder), rozszerzenia=WSZYSTKIE,
                szerokosc=1000, wysokosc=700) as vsc:
        vsc.page.wait_for_timeout(8000)
        vsc.wyczysc_powiadomienia()
        vsc.paleta("Create: New Jupyter Notebook", pauza=1200)
        vsc.czekaj("[...document.querySelectorAll('.notebook-toolbar-container, .notebookOverlay')]"
                   ".some(e => e.innerText.includes('Select Kernel'))", limit=120, opis="notatnik")
        vsc.page.wait_for_timeout(3000)
        vsc.page.mouse.move(vsc.szerokosc / 2, vsc.wysokosc - 5)
        vsc.wyczysc_powiadomienia()
        vsc.page.wait_for_timeout(800)
        vsc.podglad(vsc.nazwa)
        edytor = vsc.prostokat(".part.editor")
        komorka = vsc.prostokat(".notebookOverlay .cell-list-container .monaco-list-row")
        vsc.kadr(ZRZUTY / "zastosowania/01-jupyter/img/vsc-notatnik-nowy.png",
                 edytor["x"], edytor["y"], edytor["width"], komorka["y"] + komorka["height"] + 24 - edytor["y"])
        przycisk = vsc.page.get_by_text("Select Kernel", exact=True).first
        przycisk.click()
        vsc.page.wait_for_selector(".quick-input-widget", state="visible", timeout=30_000)
        vsc.page.wait_for_timeout(2500)
        print(f"[{vsc.nazwa}] lista 1: {opis_quick_pick(vsc)!r}")
        vsc.kadr_listy(WARIANTY / "vsc-notatnik-jadro-zrodlo.png")
        wybierz_z_listy(vsc, "Python Environments")
        vsc.czekaj("[...document.querySelectorAll('.quick-input-widget .monaco-list-row')]"
                   ".some(r => r.innerText.includes('.venv'))", limit=120, opis="pozycja .venv")
        vsc.page.wait_for_timeout(2500)
        vsc.page.mouse.move(vsc.szerokosc / 2, vsc.wysokosc - 5)
        print(f"[{vsc.nazwa}] lista 2: {opis_quick_pick(vsc)!r}")
        vsc.kadr_listy(ZRZUTY / "zastosowania/01-jupyter/img/vsc-notatnik-jadro.png")
        vsc.podglad(vsc.nazwa + "-jadro")
        vsc.klawisz("Escape")


SCENARIUSZE["15"] = jupyter


def main() -> None:
    global ZRZUTY, WARIANTY
    argumenty = [a for a in sys.argv[1:] if not a.startswith("--")]
    opcje = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--"))
    if "motyw" in opcje:
        USTAWIENIA_BAZOWE["workbench.colorTheme"] = opcje["motyw"]
    if "wyjscie" in opcje:
        ZRZUTY = Path(opcje["wyjscie"]) / "zrzuty"
        WARIANTY = Path(opcje["wyjscie"]) / "warianty"
    polecenie, *reszta = argumenty or ["zrzuty"]
    if polecenie == "projekty":
        projekty()
    elif polecenie == "proba":
        proba()
    elif polecenie == "zrzuty":
        wykonane = []  # menedzer powstaje w scenariuszu interpreter, 11 i 12 w sesji 10, a 15 w sesji 14
        for identyfikator in reszta or list(SCENARIUSZE):
            funkcja = SCENARIUSZE[identyfikator]
            if funkcja not in wykonane:
                wykonane.append(funkcja)
                funkcja()
    else:
        sys.exit(f"nieznane polecenie: {polecenie}")


if __name__ == "__main__":
    main()
