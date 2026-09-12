"""Weryfikacja wykonywalna strony Markdown: uruchamia bloki ```python title="X.py"``` i porównuje
z następującym po nich blokiem ```{ .text .no-copy }```; bloki REPL ```{ .python .no-copy }``` uruchamia
przez python -i i wypisuje rzeczywisty wynik do porównania ręcznego.

Użycie: python verify_page.py <plik.md> [interpreter]
"""
import sys, re, subprocess, pathlib, tempfile, os

sys.stdout.reconfigure(encoding="utf-8")
page = pathlib.Path(sys.argv[1])
PY = sys.argv[2] if len(sys.argv) > 2 else sys.executable
# --stdin nazwa.py=w1|w2|w3 : wiersze podawane skryptowi na stdin; w bloku wyniku
# wiersze identyczne z wejściem (echo terminala) są pomijane przy porównaniu
STDIN = {}
for arg in sys.argv[3:]:
    if arg.startswith("--stdin="):
        name, _, lines = arg[len("--stdin="):].partition("=")
        STDIN[name] = lines.split("|")
text = page.read_text(encoding="utf-8")

fence = re.compile(r"^```(?P<info>[^\n]*)\n(?P<body>.*?)^```", re.S | re.M)
blocks = [(m.group("info").strip(), m.group("body")) for m in fence.finditer(text)]
print(f"{page.name}: {len(blocks)} bloków kodu")

tmp = pathlib.Path(tempfile.mkdtemp(prefix="verify_"))
ok = fail = 0
i = 0
while i < len(blocks):
    info, body = blocks[i]
    m = re.match(r'python\s+title="([^"]+)"', info)
    if m:
        name = m.group(1)
        path = tmp / name
        path.write_text(body, encoding="utf-8")
        stdin_lines = STDIN.get(name)
        r = subprocess.run([PY, "-X", "utf8", str(path)], capture_output=True, text=True, encoding="utf-8", cwd=tmp,
                           input=("\n".join(stdin_lines) + "\n") if stdin_lines else None)
        actual = (r.stdout + r.stderr).replace(str(path), name).rstrip("\n")
        actual = re.sub(r"0x[0-9A-Fa-f]{6,}", "0x...", actual)  # adresy obiektów jako maska
        actual = actual.replace(str(tmp) + os.sep, "C:" + os.sep + "..." + os.sep + "projekt" + os.sep)  # katalog tymczasowy jako maska
        expected = None
        if i + 1 < len(blocks) and blocks[i + 1][0].startswith("{ .text .no-copy }"):
            expected = blocks[i + 1][1].rstrip("\n")
            if stdin_lines:
                pending = list(stdin_lines)
                kept = []
                for line in expected.splitlines():
                    if pending and line == pending[0]:
                        pending.pop(0)
                    else:
                        kept.append(line)
                expected = "\n".join(kept)
                print(f"    (stdin dla {name}: {stdin_lines}; niedopasowane wiersze wejścia: {pending})")
            i += 1
        if expected is None:
            print(f"\n--- {name}: brak bloku wyniku; rc={r.returncode}\n{actual}")
        elif actual == expected:
            ok += 1
            print(f"\n--- {name}: ZGODNE (rc={r.returncode})")
        else:
            fail += 1
            print(f"\n--- {name}: ROZBIEŻNOŚĆ (rc={r.returncode})\n>>> oczekiwane:\n{expected}\n>>> rzeczywiste:\n{actual}")
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
