"""Gera as páginas municipais (lavouras, pecuária, florestas) a partir de um modelo único.

Uso: python ferramentas/gerar_paginas.py
Edite o MODELO ou a lista PAGINAS e rode de novo; as páginas em src/ são sobrescritas.
"""
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"

PAGINAS = {
    "lavouras": {
        "titulo": "Lavouras",
        "intro": "Área plantada, área colhida, quantidade produzida, rendimento médio e valor da produção das lavouras temporárias e permanentes, por município de Mato Grosso do Sul.",
        "anexos": {"pam": "data/pam.parquet"},
        "conjuntos": [
            {"tabela": "pam", "nome": "Lavouras temporárias e permanentes", "pesquisa": "Produção Agrícola Municipal (PAM)", "sidra": 5457,
             "categoria": "Produto", "padraoCat": "Soja (em grão)", "padraoVar": "Quantidade produzida"},
        ],
    },
    "pecuaria": {
        "titulo": "Pecuária",
        "intro": "Efetivo dos rebanhos e produção de origem animal (leite, ovos, mel e outros), por município de Mato Grosso do Sul.",
        "anexos": {"rebanhos": "data/ppm_rebanhos.parquet", "origem": "data/ppm_origem_animal.parquet"},
        "conjuntos": [
            {"tabela": "rebanhos", "nome": "Efetivo dos rebanhos", "pesquisa": "Pesquisa da Pecuária Municipal (PPM)", "sidra": 3939,
             "categoria": "Tipo de rebanho", "padraoCat": "Bovino", "padraoVar": "Efetivo dos rebanhos"},
            {"tabela": "origem", "nome": "Produção de origem animal", "pesquisa": "Pesquisa da Pecuária Municipal (PPM)", "sidra": 74,
             "categoria": "Produto", "padraoCat": "Leite", "padraoVar": "Produção de origem animal"},
        ],
    },
    "florestas": {
        "titulo": "Florestas plantadas",
        "intro": "Área de florestas plantadas por espécie e produção da silvicultura (madeira, carvão, lenha e outros), por município de Mato Grosso do Sul.",
        "anexos": {"area": "data/pevs_area.parquet", "producao": "data/pevs_producao.parquet"},
        "conjuntos": [
            {"tabela": "area", "nome": "Área de florestas plantadas", "pesquisa": "Produção da Extração Vegetal e da Silvicultura (PEVS)", "sidra": 5930,
             "categoria": "Espécie florestal", "padraoCat": "Eucalipto", "padraoVar": "Área total existente em 31/12 dos efetivos da silvicultura"},
            {"tabela": "producao", "nome": "Produção da silvicultura", "pesquisa": "Produção da Extração Vegetal e da Silvicultura (PEVS)", "sidra": 291,
             "categoria": "Produto", "padraoCat": "1.3 - Madeira em tora", "padraoVar": "Quantidade produzida na silvicultura"},
        ],
    },
}

MODELO = r'''---
title: __TITULO__
---

# __TITULO__

<p class="nota">__INTRO__ Dados do IBGE como publicados, sem tratamento.</p>

```js
import {mapaMunicipal, baixarCSV, baixarSVG, baixarPNG, botao, fmt, slug, consulta} from "./components/util.js";
const geo = await FileAttachment("data/ms_municipios.json").json();
const db = await DuckDBClient.of({__ANEXOS__});
const CONJUNTOS = __CONJUNTOS__;
```

```js
const inConj = Inputs.radio(CONJUNTOS, {label: "Conjunto de dados", format: (d) => d.nome, value: CONJUNTOS[0]});
const conjunto = Generators.input(inConj);
```

```js
const T = conjunto.tabela;
const categorias = (await consulta(db, `select distinct categoria from ${T} order by categoria`)).map((d) => d.categoria);
const variaveis = (await consulta(db, `select distinct variavel from ${T} order by variavel`)).map((d) => d.variavel);
const inCat = Inputs.select(categorias, {label: conjunto.categoria, value: categorias.includes(conjunto.padraoCat) ? conjunto.padraoCat : categorias[0]});
const inVar = Inputs.select(variaveis, {label: "Variável", value: variaveis.includes(conjunto.padraoVar) ? conjunto.padraoVar : variaveis[0]});
const categoria = Generators.input(inCat);
const variavel = Generators.input(inVar);
```

```js
const anos = (await consulta(db, `select distinct periodo from ${T} where categoria = ? and variavel = ? order by periodo desc`, [categoria, variavel])).map((d) => d.periodo);
const inAno = Inputs.select(anos, {label: "Ano"});
const ano = Generators.input(inAno);
```

<div class="filtros">${CONJUNTOS.length > 1 ? inConj : ""}${inCat}${inVar}${inAno}</div>

```js
const linhas = [...await consulta(db, `select localidade, cod_ibge, periodo, variavel, categoria, valor, valor_num, unidade from ${T} where categoria = ? and variavel = ? and periodo = ? order by valor_num desc nulls last, localidade`, [categoria, variavel, ano])];
const unidade = linhas[0]?.unidade ?? "";
const larguraMapa = Math.max(300, Math.min(620, width > 900 ? (width - 48) / 2 : width - 32));
const mapa = mapaMunicipal(geo, linhas, {width: larguraMapa, unidade});
const tabela = Inputs.table(linhas, {
  columns: ["localidade", "cod_ibge", "valor_num"],
  header: {localidade: "Município", cod_ibge: "Código IBGE", valor_num: unidade || "Valor"},
  format: {valor_num: (v, i, d) => (v == null ? d[i].valor : fmt(v))},
  rows: 22, layout: "auto"
});
const colunasCSV = [
  {campo: "localidade", titulo: "Município"}, {campo: "cod_ibge", titulo: "Código IBGE"}, {campo: "periodo", titulo: "Ano"},
  {campo: "categoria", titulo: conjunto.categoria}, {campo: "variavel", titulo: "Variável"},
  {campo: "valor", titulo: "Valor"}, {campo: "unidade", titulo: "Unidade"}
];
const nomeBase = `${slug(conjunto.nome)}_${slug(categoria)}_${slug(variavel)}`;
```

<div class="grid grid-cols-2">
  <div class="card">
    <h2>${categoria}, ${ano}</h2>
    <p class="fonte">${variavel}${unidade ? ` (${unidade})` : ""}. Municípios em cinza: sem registro na pesquisa ou valor sob sigilo.</p>
    ${mapa}
    <div class="botoes">${botao("Baixar mapa (PNG)", () => baixarPNG(mapa, `mapa_${nomeBase}_${ano}.png`))}${botao("Baixar mapa (SVG)", () => baixarSVG(mapa, `mapa_${nomeBase}_${ano}.svg`))}</div>
  </div>
  <div class="card">
    <h2>Municípios (${linhas.length})</h2>
    ${tabela}
    <div class="botoes">${botao("Baixar esta tabela (CSV)", () => baixarCSV(linhas, colunasCSV, `${nomeBase}_${ano}.csv`))}${botao("Baixar todos os anos (CSV)", async () => baixarCSV([...await consulta(db, `select * from ${T} where categoria = ? and variavel = ? order by periodo, localidade`, [categoria, variavel])], colunasCSV, `${nomeBase}_todos_os_anos.csv`))}</div>
  </div>
</div>

## Série histórica por município

```js
const municipios = geo.features.map((f) => f.properties.name).sort((a, b) => a.localeCompare(b, "pt-BR"));
const inMun = Inputs.select(municipios, {label: "Município", value: linhas[0]?.localidade ?? municipios[0]});
const municipio = Generators.input(inMun);
```

<div class="filtros">${inMun}</div>

```js
const serie = [...await consulta(db, `select localidade, cod_ibge, periodo, variavel, categoria, valor, valor_num, unidade from ${T} where categoria = ? and variavel = ? and localidade = ? order by periodo`, [categoria, variavel, municipio])];
```

<div class="card">
  <h2>${municipio}: ${categoria}</h2>
  <p class="fonte">${variavel}. Anos sem barra: sem registro na pesquisa.${variavel.startsWith("Valor") ? " Valores em moeda corrente de cada ano, sem correção; ver a coluna Unidade do arquivo." : ""}</p>
  ${serie.length ? resize((w) => Plot.plot({
    width: w, height: 300, marginLeft: 70,
    x: {label: null, tickFormat: (d) => d, type: "band"},
    y: {label: serie.at(-1).unidade, grid: true, tickFormat: (v) => fmt(v)},
    marks: [
      Plot.barY(serie.filter((d) => d.valor_num != null), {x: "periodo", y: "valor_num", fill: "#004f9f", tip: {format: {y: (v) => fmt(v)}}}),
      Plot.ruleY([0])
    ]
  })) : html`<p class="nota">Sem registros para este município.</p>`}
  <div class="botoes">${botao("Baixar série do município (CSV)", () => baixarCSV(serie, colunasCSV, `${nomeBase}_${slug(municipio)}.csv`))}</div>
</div>

<p class="fonte">Fonte: IBGE, ${conjunto.pesquisa}, tabela SIDRA ${conjunto.sidra}. Ausência de registro equivale a zero; "X" indica valor sob sigilo.</p>
'''


def js_obj(d: dict) -> str:
    import json
    return json.dumps(d, ensure_ascii=False)


for nome, p in PAGINAS.items():
    anexos = ", ".join(f'{k}: FileAttachment("{v}")' for k, v in p["anexos"].items())
    texto = (MODELO.replace("__TITULO__", p["titulo"]).replace("__INTRO__", p["intro"])
             .replace("__ANEXOS__", anexos).replace("__CONJUNTOS__", js_obj(p["conjuntos"])))
    (SRC / f"{nome}.md").write_text(texto, encoding="utf-8")
    print("gerada", nome)
