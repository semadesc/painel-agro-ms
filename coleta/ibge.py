"""Coleta de tabelas do IBGE (API de agregados v3) para Mato Grosso do Sul.

Grava os valores como o IBGE publica, sem tratamento: um CSV por tabela e por
período em data/ibge/<pesquisa>/<tabela>/. Ficam de fora apenas as células
vazias ou zero (a ausência da linha equivale a zero) e os percentuais
calculados pelo IBGE. O sigilo ("X") é mantido na coluna "valor".

Uso:
    python coleta/ibge.py              # atualiza tudo (incremental)
    python coleta/ibge.py pam ppm      # só as pesquisas indicadas
    python coleta/ibge.py --completo   # baixa de novo todos os períodos
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

import requests

API = "https://servicodados.ibge.gov.br/api/v3/agregados"
RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "data" / "ibge"
UF = "50"  # Mato Grosso do Sul

# pesquisa -> tabelas SIDRA, nível territorial e quantos períodos por consulta
TABELAS = {
    "pam": [
        {"tabela": 5457, "nome": "lavouras", "nivel": "municipio", "lote": 1},
    ],
    "ppm": [
        {"tabela": 3939, "nome": "rebanhos", "nivel": "municipio", "lote": 1},
        {"tabela": 74, "nome": "producao_origem_animal", "nivel": "municipio", "lote": 1},
    ],
    "pevs": [
        {"tabela": 5930, "nome": "area_silvicultura", "nivel": "municipio", "lote": 1},
        {"tabela": 291, "nome": "producao_silvicultura", "nivel": "municipio", "lote": 1},
    ],
    "lspa": [
        {"tabela": 6588, "nome": "estimativa_safra", "nivel": "estado", "lote": 12},
    ],
}
LOCALIDADE = {"municipio": f"N6[N3[{UF}]]", "estado": f"N3[{UF}]"}
REFAZER_ULTIMOS = 3  # períodos mais recentes sempre baixados de novo (revisões do IBGE)

COLUNAS = ["tabela", "periodo", "nivel", "cod_ibge", "localidade", "variavel_id", "variavel",
           "unidade", "classificacao", "categoria_id", "categoria", "valor"]

sessao = requests.Session()
sessao.headers["User-Agent"] = "painel-agro-ms (github.com/semadesc/painel-agro-ms)"


def get(url: str, params: dict | None = None, tentativas: int = 5):
    for i in range(tentativas):
        try:
            r = sessao.get(url, params=params, timeout=180)
            if r.status_code == 200:
                return r.json()
            erro = f"HTTP {r.status_code}: {r.text[:200]}"
        except requests.RequestException as e:
            erro = str(e)
        espera = 5 * (i + 1)
        print(f"    falha ({erro}); nova tentativa em {espera}s", flush=True)
        time.sleep(espera)
    raise RuntimeError(f"Não foi possível obter {url} {params}")


def baixar_periodos(cfg: dict, meta: dict, periodos: list[str]) -> list[dict]:
    variaveis = "|".join(str(v["id"]) for v in meta["variaveis"])
    classif = "|".join(f"{c['id']}[all]" for c in meta["classificacoes"])
    params = {"localidades": LOCALIDADE[cfg["nivel"]]}
    if classif:
        params["classificacao"] = classif
    url = f"{API}/{cfg['tabela']}/periodos/{'|'.join(periodos)}/variaveis/{variaveis}"
    dados = get(url, params)
    linhas = []
    for var in dados:
        for res in var["resultados"]:
            cats = res.get("classificacoes", [])
            classificacao = "; ".join(c["nome"] for c in cats)
            cat_ids = "; ".join(next(iter(c["categoria"].keys())) for c in cats)
            cat_nomes = "; ".join(next(iter(c["categoria"].values())) for c in cats)
            for s in res["series"]:
                loc = s["localidade"]
                for periodo, valor in s["serie"].items():
                    linhas.append({
                        "tabela": cfg["tabela"], "periodo": periodo, "nivel": loc["nivel"]["nome"],
                        "cod_ibge": loc["id"], "localidade": loc["nome"], "variavel_id": var["id"],
                        "variavel": var["variavel"], "unidade": var["unidade"],
                        "classificacao": classificacao, "categoria_id": cat_ids,
                        "categoria": cat_nomes, "valor": valor,
                    })
    return linhas


def gravar(caminho: Path, linhas: list[dict]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    # Para manter o repositório leve: descarta células sem dado ("..", "..."),
    # zeros absolutos ("-", a ausência da linha equivale a zero) e as variáveis
    # de percentual calculadas pelo IBGE (ids a partir de 1000000). Mantém o sigilo ("X").
    linhas = [l for l in linhas
              if l["valor"] not in ("..", "...", "-", None) and int(l["variavel_id"]) < 1000000]
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS)
        w.writeheader()
        w.writerows(linhas)


def coletar(pesquisa: str, completo: bool) -> None:
    for cfg in TABELAS[pesquisa]:
        t = cfg["tabela"]
        print(f"[{pesquisa}] tabela {t} ({cfg['nome']})", flush=True)
        meta = get(f"{API}/{t}/metadados")
        periodos = [p["id"] for p in get(f"{API}/{t}/periodos")]
        pasta = DESTINO / pesquisa / cfg["nome"]
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / "metadados.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

        recentes = set(periodos[-REFAZER_ULTIMOS:])
        pendentes = [p for p in periodos if completo or p in recentes
                     or not (pasta / f"{cfg['nome']}_{p}.csv").exists()]
        print(f"  {len(periodos)} períodos ({periodos[0]} a {periodos[-1]}); a baixar: {len(pendentes)}", flush=True)
        for i in range(0, len(pendentes), cfg["lote"]):
            lote = pendentes[i:i + cfg["lote"]]
            linhas = baixar_periodos(cfg, meta, lote)
            for p in lote:
                doperiodo = [l for l in linhas if l["periodo"] == p]
                gravar(pasta / f"{cfg['nome']}_{p}.csv", doperiodo)
            print(f"  {lote[0]}{'..' + lote[-1] if len(lote) > 1 else ''}: {len(linhas)} linhas", flush=True)
            time.sleep(0.5)


def main(args: list[str]) -> None:
    completo = "--completo" in args
    escolhidas = [a for a in args if not a.startswith("--")] or list(TABELAS)
    for p in escolhidas:
        coletar(p, completo)


if __name__ == "__main__":
    main(sys.argv[1:])
