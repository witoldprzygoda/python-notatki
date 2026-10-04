"""Renderuje strumień VT z przechwyc.py w xterm.js ze schematem kolorów Windows Terminal i zapisuje PNG.

Użycie:
    python renderuj.py <wejście.vt> <wyjście.png> [schemat]

Przykład (rozdział 2 części „Python Podstawy”):
    python przechwyc.py C:/Users/<użytkownik>/AppData/Local/Python/pythoncore-3.14-64/python.exe %TEMP%/repl.vt
    python renderuj.py %TEMP%/repl.vt docs/02-konsola/img/repl-kolorowanie.png

Schemat: one-half-light (domyślny, decyzja autora z 2 X 2026) albo campbell. Pogrubienie
rysujemy zwykłymi kolorami schematu, jak Windows Terminal z ustawieniem
intenseTextStyle: "bold". Wysokość obrazu obejmuje wiersze do ostatniego niepustego.

Przygotowanie (jednorazowo, w tym katalogu; pobrane pliki wyklucza lokalny .gitignore):
    npm install                       — xterm.js w wersji z package-lock.json;
    czcionka Cascadia Mono            — z wydania Cascadia Code
                                        (github.com/microsoft/cascadia-code/releases),
                                        plik ttf/CascadiaMono.ttf rozpakowany do cascadia/ttf/.
Uruchamiać interpreterem środowiska narzędzi z pakietem playwright (przeglądarka Microsoft Edge
bez okna). Strona pomocnicza render.html powstaje na czas renderowania i jest potem usuwana.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

TU = Path(__file__).resolve().parent
KOLUMNY, WIERSZE = 56, 12
SCHEMATY = {  # wbudowane schematy Windows Terminal (src/cascadia/TerminalSettingsModel/defaults.json)
    "campbell": {
        "background": "#0C0C0C", "foreground": "#CCCCCC", "cursor": "#FFFFFF",
        "black": "#0C0C0C", "red": "#C50F1F", "green": "#13A10E", "yellow": "#C19C00",
        "blue": "#0037DA", "magenta": "#881798", "cyan": "#3A96DD", "white": "#CCCCCC",
        "brightBlack": "#767676", "brightRed": "#E74856", "brightGreen": "#16C60C", "brightYellow": "#F9F1A5",
        "brightBlue": "#3B78FF", "brightMagenta": "#B4009E", "brightCyan": "#61D6D6", "brightWhite": "#F2F2F2",
    },
    "one-half-light": {
        "background": "#FAFAFA", "foreground": "#383A42", "cursor": "#4F525D",
        "black": "#383A42", "red": "#E45649", "green": "#50A14F", "yellow": "#C18301",
        "blue": "#0184BC", "magenta": "#A626A4", "cyan": "#0997B3", "white": "#FAFAFA",
        "brightBlack": "#4F525D", "brightRed": "#DF6C75", "brightGreen": "#98C379", "brightYellow": "#E4C07A",
        "brightBlue": "#61AFEF", "brightMagenta": "#C577DD", "brightCyan": "#56B5C1", "brightWhite": "#FFFFFF",
    },
}


def main() -> None:
    vt, wyjscie = sys.argv[1], sys.argv[2]
    schemat = SCHEMATY[sys.argv[3] if len(sys.argv) > 3 else "one-half-light"]
    for wymagany in ("node_modules/@xterm/xterm/lib/xterm.js", "cascadia/ttf/CascadiaMono.ttf"):
        if not (TU / wymagany).is_file():
            sys.exit(f"brak {TU / wymagany} — zob. „Przygotowanie” w opisie skryptu")
    strona = TU / "render.html"
    strona.write_text(f"""<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="node_modules/@xterm/xterm/css/xterm.css">
<style>
@font-face {{ font-family: "Cascadia Mono"; src: url("cascadia/ttf/CascadiaMono.ttf"); }}
html, body {{ margin: 0; background: {schemat['background']}; }}
#ramka {{ display: inline-block; padding: 10px 12px; background: {schemat['background']}; }}
</style>
<div id="ramka"><div id="terminal"></div></div>
<script src="node_modules/@xterm/xterm/lib/xterm.js"></script>
""", encoding="utf-8")
    dane = Path(vt).read_text(encoding="utf-8") + "\x1b[?25l"  # bez kursora
    try:
        with sync_playwright() as p:
            przegladarka = p.chromium.launch(channel="msedge")
            karta = przegladarka.new_page(device_scale_factor=1)
            karta.goto(strona.as_uri())
            karta.evaluate("() => document.fonts.load('16px \"Cascadia Mono\"')")
            karta.evaluate(f"""dane => new Promise(gotowe => {{
                const term = new Terminal({{cols: {KOLUMNY}, rows: {WIERSZE}, fontFamily: '"Cascadia Mono"',
                                           fontSize: 16, theme: {json.dumps(schemat)}, cursorBlink: false,
                                           convertEol: true, drawBoldTextInBrightColors: false}});
                term.open(document.getElementById("terminal"));
                term.write(dane, () => {{
                    const bufor = term.buffer.active;
                    let ostatni = 0;
                    for (let i = 0; i < bufor.length; i++) {{
                        if (bufor.getLine(i).translateToString(true).trim()) ostatni = i;
                    }}
                    term.resize({KOLUMNY}, ostatni + 1);
                    setTimeout(gotowe, 200);
                }});
            }})""", dane)
            Path(wyjscie).parent.mkdir(parents=True, exist_ok=True)
            karta.locator("#ramka").screenshot(path=wyjscie)
            przegladarka.close()
    finally:
        strona.unlink(missing_ok=True)
    print(f"zapisano {wyjscie}")


if __name__ == "__main__":
    main()
