"""Funções comuns dos carregadores de dados do site.

Os carregadores leem os CSV coletados em data/ e geram arquivos Parquet para o
navegador. Não há cálculo nem tratamento: apenas a conversão de formato e a
coluna numérica "valor_num" ao lado do valor original.
"""
import csv
import glob
import json
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "data"


def numero(texto):
    if texto is None:
        return None
    t = str(texto).strip().replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def ibge(pasta: str) -> None:
    """Consolida os CSV de uma tabela do IBGE e grava Parquet na saída padrão."""
    base = DADOS / "ibge" / pasta
    meta = json.loads((base / "metadados.json").read_text(encoding="utf-8"))
    unid_cat = {}
    for c in meta.get("classificacoes", []):
        for cat in c["categorias"]:
            if cat.get("unidade"):
                unid_cat[cat["nome"]] = cat["unidade"]
    col = {k: [] for k in ["periodo", "cod_ibge", "localidade", "variavel", "categoria", "unidade", "valor", "valor_num"]}
    for arq in sorted(glob.glob(str(base / "*.csv"))):
        with open(arq, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                col["periodo"].append(r["periodo"])
                col["cod_ibge"].append(r["cod_ibge"])
                col["localidade"].append(r["localidade"].removesuffix(" - MS"))
                col["variavel"].append(r["variavel"])
                col["categoria"].append(r["categoria"])
                col["unidade"].append(r["unidade"] or unid_cat.get(r["categoria"], ""))
                col["valor"].append(r["valor"])
                col["valor_num"].append(numero(r["valor"]))
    gravar(pa.table(col))


def conab(arquivo: str) -> None:
    """Converte um arquivo da CONAB (já filtrado para MS) em Parquet."""
    with open(DADOS / "conab" / arquivo, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    if not linhas:
        gravar(pa.table({}))
        return
    col = {}
    for k in linhas[0]:
        valores = [r[k] for r in linhas]
        nums = [numero(v) for v in valores]
        eh_num = k not in ("ano_agricola", "id_produto", "id_levantamento") and all(
            n is not None or v == "" for n, v in zip(nums, valores))
        col[k] = nums if eh_num else valores
    gravar(pa.table(col))


def gravar(tabela: pa.Table) -> None:
    buf = pa.BufferOutputStream()
    pq.write_table(tabela, buf, compression="zstd")
    sys.stdout.buffer.write(buf.getvalue().to_pybytes())
