"""Coleta dos arquivos de dados da CONAB (Portal de Informações Agropecuárias).

Baixa os arquivos nacionais, mantém só as linhas de Mato Grosso do Sul e grava
em data/conab/ com as mesmas colunas e valores do arquivo original.

Uso:
    python coleta/conab.py
"""
from __future__ import annotations

import csv
import io
import sys
import time
from pathlib import Path

import requests

BASE = "https://portaldeinformacoes.conab.gov.br/downloads/arquivos/"
RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "data" / "conab"
UF = "MS"

ARQUIVOS = {
    "levantamento_graos": "LevantamentoGraos.txt",
    "serie_historica_graos": "SerieHistoricaGraos.txt",
    "levantamento_cana": "LevantamentoCana.txt",
    "serie_historica_cana": "SerieHistoricaCana.txt",
}

sessao = requests.Session()
sessao.headers["User-Agent"] = "painel-agro-ms (github.com/semadesc/painel-agro-ms)"


def baixar(nome_arquivo: str) -> str | None:
    url = BASE + nome_arquivo
    for i in range(4):
        try:
            r = sessao.get(url, timeout=300)
            if r.status_code == 200 and r.content:
                for enc in ("utf-8-sig", "latin-1"):
                    try:
                        return r.content.decode(enc)
                    except UnicodeDecodeError:
                        continue
            print(f"  {url}: HTTP {r.status_code}", flush=True)
            if r.status_code == 404:
                return None
        except requests.RequestException as e:
            print(f"  {url}: {e}", flush=True)
        time.sleep(10 * (i + 1))
    return None


def filtrar_uf(texto: str) -> tuple[list[str], list[list[str]], str]:
    amostra = texto[:5000]
    sep = ";" if amostra.count(";") > amostra.count(",") else ","
    leitor = csv.reader(io.StringIO(texto), delimiter=sep)
    cab = [c.strip() for c in next(leitor)]
    col_uf = next((i for i, c in enumerate(cab) if c.lower() in ("uf", "sigla_uf", "estado")), None)
    # remove só os espaços de preenchimento do arquivo original; os valores não mudam
    linhas = [[c.strip() for c in l] for l in leitor
              if l and (col_uf is None or l[col_uf].strip().upper() == UF)]
    return cab, linhas, sep


def main() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    ok = 0
    for chave, arquivo in ARQUIVOS.items():
        print(f"[conab] {arquivo}", flush=True)
        texto = baixar(arquivo)
        if texto is None:
            print("  não disponível", flush=True)
            continue
        cab, linhas, sep = filtrar_uf(texto)
        print(f"  colunas: {cab}", flush=True)
        print(f"  linhas de {UF}: {len(linhas)}", flush=True)
        if linhas:
            print(f"  exemplo: {linhas[-1]}", flush=True)
        with open(DESTINO / f"{chave}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(cab)
            w.writerows(linhas)
        ok += 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
