"""Weryfikacja wykonywalna strony Markdown.

Uruchamia bloki ```python title="X.py"``` w katalogu tymczasowym i porównuje ich wyjście
z blokiem ```{ .text .no-copy }``` następującym BEZPOŚREDNIO po nich (bez prozy pomiędzy).
Strumienie stdout i stderr są łączone w kolejności, w jakiej widzi je terminal
(interpreter uruchamiany z -u). Bloki z title= w innym języku (text, json, toml, ...)
są zapisywane jako pliki danych w katalogu tymczasowym w kolejności występowania,
zanim uruchomione zostaną kolejne skrypty (np. ```text title="dane.txt"```). Bloki
```powershell/bash title="Terminal"``` są pomijane. Bloki REPL ```{ .python .no-copy }```
są uruchamiane przez python -i, a ich rzeczywisty wynik wypisywany do porównania ręcznego.

Użycie: python scripts/verify_page.py <plik.md> [interpreter]
           [--stdin=nazwa.py=w1|w2|w3] [--mask=REGEX] [--data=katalog] [--skip=nazwa.py,...]

--stdin: wiersze podawane skryptowi jako odpowiedzi na kolejne wywołania input();
skrypt jest wtedy uruchamiany przez runner, który — jak terminal — wypisuje po
zachęcie wpisany tekst i znak nowego wiersza, więc blok wyniku może być dosłownym
zapisem sesji terminalowej.
--mask: wyrażenie regularne; dopasowane fragmenty są zastępowane znacznikiem
<MASKA> zarówno w wyniku rzeczywistym, jak i oczekiwanym (np. czasy pomiarów, daty).
Skrypty są uruchamiane z zamkniętym stdin (breakpoint() kończy się natychmiast).
--data: katalog, którego pliki (z podkatalogami) są kopiowane do katalogu tymczasowego przed uruchomieniem
skryptów (wspólne pliki danych rozdziału, których strona nie osadza jako bloków).
--skip: nazwy skryptów, które są tylko zapisywane, nie uruchamiane (np. moduł z blokiem
__main__ uruchamiającym serwer bez końca); blok wyniku po takim skrypcie jest pomijany.
"""
import sys, re, subprocess, pathlib, tempfile, os

sys.stdout.reconfigure(encoding="utf-8")
page = pathlib.Path(sys.argv[1])
PY = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else sys.executable
STDIN = {}
DATA = None  # katalog z plikami danych kopiowanymi do katalogu tymczasowego (--data=)
MASKS = [r"0x[0-9A-Fa-f]{6,}"]  # adresy obiektów
SKIP = set()  # skrypty tylko zapisywane (--skip=)
for arg in sys.argv[2:]:
    if arg.startswith("--stdin="):
        name, _, lines = arg[len("--stdin="):].partition("=")
        STDIN[name] = lines.split("|")
    elif arg.startswith("--mask="):
        MASKS.append(arg[len("--mask="):])
    elif arg.startswith("--data="):
        DATA = pathlib.Path(arg[len("--data="):])
    elif arg.startswith("--skip="):
        SKIP.update(arg[len("--skip="):].split(","))
text = page.read_text(encoding="utf-8")

RUNNER = '''import builtins, runpy, sys
odpowiedzi = sys.argv[2].split("|")
def input_echo(prompt=""):
    print(prompt, end="", flush=True)
    if not odpowiedzi:
        raise EOFError
    wiersz = odpowiedzi.pop(0)
    print(wiersz, flush=True)
    return wiersz
builtins.input = input_echo
runpy.run_path(sys.argv[1], run_name="__main__")
'''


def mask(s):
    for m in MASKS:
        s = re.sub(m, "<MASKA>", s)
    return s


fence = re.compile(r"^```(?P<info>[^\n]*)\n(?P<body>.*?)^```", re.S | re.M)
matches = list(fence.finditer(text))
blocks = [(m.group("info").strip(), m.group("body"), m.start(), m.end()) for m in matches]
print(f"{page.name}: {len(blocks)} bloków kodu")


def follows_directly(i):
    """Czy blok i+1 następuje bezpośrednio po bloku i (tylko białe znaki pomiędzy)."""
    return i + 1 < len(blocks) and text[blocks[i][3]:blocks[i + 1][2]].strip() == ""


tmp = pathlib.Path(tempfile.mkdtemp(prefix="verify_"))
if DATA:
    for f in DATA.rglob("*"):
        if f.is_file():
            cel = tmp / f.relative_to(DATA)
            cel.parent.mkdir(parents=True, exist_ok=True)
            cel.write_bytes(f.read_bytes())
runner = tmp / "_runner.py"
runner.write_text(RUNNER, encoding="utf-8")
ok = fail = 0
i = 0
while i < len(blocks):
    info, body, _, _ = blocks[i]
    m = re.match(r'python\s+title="([^"]+)"', info)
    data = re.match(r'(\w+)\s+title="([^"]+)"', info)
    if m and ".ipynb" in m.group(1):
        print(f"\n--- {m.group(1)}: komórka notatnika — pomijam (weryfikuje verify_cells.py)")
    elif m:
        name = m.group(1)
        path = tmp / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        if name in SKIP:
            print(f"\n--- {name}: zapisany, nieuruchamiany (--skip)")
            if follows_directly(i) and blocks[i + 1][0].startswith("{ .text .no-copy }"):
                i += 1
            i += 1
            continue
        stdin_lines = STDIN.get(name)
        if stdin_lines:
            cmd = [PY, "-X", "utf8", "-u", str(runner), str(path), "|".join(stdin_lines)]
        else:
            cmd = [PY, "-X", "utf8", "-u", str(path)]
        r = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, encoding="utf-8", cwd=tmp)
        actual = r.stdout.replace(str(path), name).rstrip("\n")
        actual = actual.replace(str(tmp) + os.sep, "C:" + os.sep + "..." + os.sep + "projekt" + os.sep)
        actual = mask(actual)
        expected = None
        if follows_directly(i) and blocks[i + 1][0].startswith("{ .text .no-copy }"):
            expected = mask(blocks[i + 1][1].rstrip("\n"))
            i += 1
        if expected is None:
            print(f"\n--- {name}: brak bloku wyniku; rc={r.returncode}\n{actual}")
        elif actual == expected:
            ok += 1
            print(f"\n--- {name}: ZGODNE (rc={r.returncode})")
        else:
            fail += 1
            print(f"\n--- {name}: ROZBIEŻNOŚĆ (rc={r.returncode})\n>>> oczekiwane:\n{expected}\n>>> rzeczywiste:\n{actual}")
    elif data and data.group(1) not in ("powershell", "bash", "console") and "." in data.group(2):
        name = data.group(2)
        (tmp / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp / name).write_text(body, encoding="utf-8")
        print(f"\n--- plik danych zapisany: {name} ({len(body.splitlines())} wierszy)")
    elif info.startswith("{ .python .no-copy }") and ">>>" in body:
        inputs = []
        for line in body.splitlines():
            if line.startswith(">>> "):
                inputs.append(line[4:])
            elif line.startswith("... "):
                inputs.append(line[4:])
            elif line == "...":
                inputs.append("")
        src = "\n".join(inputs) + "\n"
        r = subprocess.run([PY, "-X", "utf8", "-i", "-q"], input=src, capture_output=True, text=True, encoding="utf-8", cwd=tmp)
        out = (r.stdout + "\n[stderr]\n" + r.stderr).rstrip()
        print(f"\n--- blok REPL #{i + 1} (wejście {len(inputs)} linii) — wynik rzeczywisty (-i, nazwa pliku <stdin> zamiast <python-input-N>):\n{out}")
    i += 1
print(f"\nSKRYPTY: zgodne {ok}, rozbieżne {fail}")
