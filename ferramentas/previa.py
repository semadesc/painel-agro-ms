"""Abre cada página do site montado (dist/) num navegador e salva capturas e erros.

Uso (com o site servido em http://localhost:8000): python ferramentas/previa.py previa/
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PAGINAS = ["index", "lavouras", "pecuaria", "florestas", "conab", "lspa", "dados"]
saida = Path(sys.argv[1])
saida.mkdir(parents=True, exist_ok=True)
log = []
with sync_playwright() as p:
    nav = p.chromium.launch()
    for largura, sufixo in [(1366, ""), (390, "_celular")]:
        pg = nav.new_page(viewport={"width": largura, "height": 900})
        erros = []
        pg.on("pageerror", lambda e: erros.append(f"pageerror: {e}"))
        pg.on("console", lambda m: erros.append(f"console.{m.type}: {m.text}") if m.type in ("error", "warning") else None)
        for nome in PAGINAS:
            erros.clear()
            pg.goto(f"http://localhost:8000/{nome}.html", wait_until="networkidle")
            pg.wait_for_timeout(6000)
            pg.screenshot(path=str(saida / f"{nome}{sufixo}.png"), full_page=True)
            erros_tela = pg.eval_on_selector_all(".observablehq--error", "els => els.map(e => e.textContent)")
            log.append(f"== {nome}{sufixo}")
            log.extend(erros)
            log.extend(f"erro na célula: {t}" for t in erros_tela)
        pg.close()
    nav.close()
(saida / "log.txt").write_text("\n".join(log), encoding="utf-8")
print("\n".join(log))
