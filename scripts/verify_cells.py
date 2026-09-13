"""Weryfikacja komórek notatników w stronie MkDocs.

Bloki ```python title="<nazwa>.ipynb — komórka N"``` tej samej nazwy są składane w notatnik
i wykonywane w kolejności w jądrze Jupyter (nbclient, jądro python3 bieżącego interpretera).
Wynik komórki (strumień stdout/stderr + text/plain wartości ostatniego wyrażenia + błędy)
jest porównywany z bezpośrednio następującym blokiem ```{ .text .no-copy }```.
Bloki ```<lang> title="plik"``` (text, csv, json...) są zapisywane jako pliki danych.
Pliki PNG utworzone przez komórki są kopiowane do katalogu --img (jeśli podano).
Użycie: python verify_cells.py <strona.md> [--mask=REGEX ...] [--img=katalog] [--refresh] [--cwd=PODKATALOG]
  --cwd      jądro pracuje w podkatalogu katalogu projektu (np. notatniki), pliki danych leżą w projekcie.
  Bloki ```python title="plik.py"``` niebędące komórkami są zapisywane jako moduły pomocnicze.
  --refresh  zastępuje bloki oczekiwane rzeczywistym wynikiem (bez masek).
"""
import re, sys, pathlib, tempfile, shutil, os, asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import nbformat
from nbclient import NotebookClient

args = [a for a in sys.argv[1:] if not a.startswith("--")]
opts = [a for a in sys.argv[1:] if a.startswith("--")]
page = pathlib.Path(args[0])
masks = [o[len("--mask="):] for o in opts if o.startswith("--mask=")]
img_dir = next((pathlib.Path(o[len("--img="):]) for o in opts if o.startswith("--img=")), None)
refresh = "--refresh" in opts
cwd_sub = next((o[len("--cwd="):] for o in opts if o.startswith("--cwd=")), "")
text = page.read_text(encoding="utf-8")
fence = re.compile(r"^```(?P<info>[^\n]*)\n(?P<body>.*?)^```", re.S | re.M)
blocks = list(fence.finditer(text))
tmp = pathlib.Path(tempfile.mkdtemp())
cell_re = re.compile(r'python title="(?P<nb>[^"]+\.ipynb) — komórka (?P<n>\d+)"')


def mask(s):
    for m in masks:
        s = re.sub(m, "<…>", s)
    return s


# pliki danych
for m in blocks:
    info = m.group("info").strip()
    d = re.match(r'(\w+)\s+title="([^"]+)"', info)
    if d and d.group(2) != "Terminal" and "." in d.group(2) and ".ipynb" not in d.group(2):
        p = tmp / d.group(2)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(m.group("body"), encoding="utf-8")

# notatniki
notebooks = {}
for i, m in enumerate(blocks):
    c = cell_re.match(m.group("info").strip())
    if not c:
        continue
    expected_idx = None
    if i + 1 < len(blocks) and blocks[i + 1].group("info").strip() == "{ .text .no-copy }" and not text[m.end():blocks[i + 1].start()].strip():
        expected_idx = i + 1
    notebooks.setdefault(c.group("nb"), []).append((int(c.group("n")), m.group("body"), expected_idx))

ok = fail = 0
replacements = []  # (start, end, new_text) w tekście strony
for nb_name, cells in notebooks.items():
    cells.sort()
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(body.rstrip("\n")) for _, body, _ in cells]
    kdir = tmp / cwd_sub if cwd_sub else tmp
    kdir.mkdir(parents=True, exist_ok=True)
    client = NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(kdir)}},
                            allow_errors=True)
    client.execute()
    for (n, body, exp_idx), cell in zip(cells, nb.cells):
        parts = []
        for out in cell.get("outputs", []):
            if out["output_type"] == "stream":
                parts.append(out["text"])
            elif out["output_type"] in ("execute_result", "display_data"):
                if "text/plain" in out.get("data", {}):
                    parts.append(out["data"]["text/plain"] + "\n")
            elif out["output_type"] == "error":
                parts.append(out["ename"] + ": " + out["evalue"] + "\n")
        actual = "".join(parts).rstrip("\n")
        actual = actual.replace(str(tmp) + os.sep, "C:" + os.sep + "..." + os.sep + "projekt" + os.sep)
        if exp_idx is None:
            print(f"--- {nb_name} [{n}]: brak bloku wyniku\n{actual}")
            continue
        exp_block = blocks[exp_idx]
        expected = exp_block.group("body").rstrip("\n")
        if refresh:
            replacements.append((exp_block.start("body"), exp_block.end("body"), actual + "\n"))
            print(f"--- {nb_name} [{n}]: odświeżono ({actual.count(chr(10)) + 1} wierszy)")
        elif mask(actual) == mask(expected):
            ok += 1
            print(f"--- {nb_name} [{n}]: ZGODNE")
        else:
            fail += 1
            print(f"--- {nb_name} [{n}]: ROZBIEŻNOŚĆ\n>>> oczekiwane:\n{expected}\n>>> rzeczywiste:\n{actual}")

if refresh and replacements:
    out = []
    last = 0
    for s, e, new in sorted(replacements):
        out.append(text[last:s]); out.append(new); last = e
    out.append(text[last:])
    page.write_text("".join(out), encoding="utf-8")

if img_dir:
    img_dir.mkdir(parents=True, exist_ok=True)
    for p in tmp.rglob("*.png"):
        shutil.copyfile(p, img_dir / p.name)
        print("obraz:", p.name)
print(f"KOMÓRKI: zgodne {ok}, rozbieżne {fail}, notatników {len(notebooks)}")
