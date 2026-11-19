---
title: Safra de grãos e cana (CONAB)
---

# Safra de grãos e cana-de-açúcar (CONAB)

<p class="nota">Estimativas da CONAB para Mato Grosso do Sul: a série histórica traz o resultado de cada safra; os levantamentos trazem cada estimativa mensal divulgada durante a safra. Dados como publicados nos arquivos da CONAB, sem tratamento.</p>

```js
import {baixarCSV, botao, fmt, slug} from "./components/util.js";
const db = await DuckDBClient.of({
  gs: FileAttachment("data/conab_serie_historica_graos.parquet"),
  gl: FileAttachment("data/conab_levantamento_graos.parquet"),
  cs: FileAttachment("data/conab_serie_historica_cana.parquet"),
  cl: FileAttachment("data/conab_levantamento_cana.parquet")
});
const ROTULOS = {
  ano_agricola: "Ano agrícola", safra: "Safra", dsc_safra_previsao: "Safra", uf: "UF", produto: "Produto", id_produto: "Código do produto",
  id_levantamento: "Nº do levantamento", dsc_levantamento: "Levantamento", dsc_situacao_levantamento: "Situação",
  area_plantada_mil_ha: "Área plantada (mil ha)", producao_mil_t: "Produção (mil t)", produtividade_mil_ha_mil_t: "Produtividade (t/ha)",
  producao_acucar_mil_t: "Açúcar (mil t)", producao_etanol_anidro_mil_l: "Etanol anidro (mil L)",
  producao_etanol_hidratado_mil_l: "Etanol hidratado (mil L)", producao_etanol_total_mil_l: "Etanol total (mil L)", produtcao_atr_kg_t: "ATR (kg/t)"
};
const CONJUNTOS = [
  {t: "gs", nome: "Grãos: série histórica", tipo: "serie"},
  {t: "gl", nome: "Grãos: levantamentos da safra", tipo: "levantamento"},
  {t: "cs", nome: "Cana-de-açúcar: série histórica", tipo: "serie"},
  {t: "cl", nome: "Cana-de-açúcar: levantamentos da safra", tipo: "levantamento"}
];
```

```js
const inConj = Inputs.radio(CONJUNTOS, {label: "Conjunto de dados", format: (d) => d.nome, value: CONJUNTOS[0]});
const conjunto = Generators.input(inConj);
```

```js
const T = conjunto.t;
const colunas = (await db.query(`describe ${T}`)).map((c) => c.column_name);
const colSafra = colunas.includes("dsc_safra_previsao") ? "dsc_safra_previsao" : "safra";
const produtos = (await db.query(`select distinct produto from ${T} order by produto`)).map((d) => d.produto);
const inProd = Inputs.select(produtos, {label: "Produto", value: produtos.includes("SOJA") ? "SOJA" : produtos[0]});
const produto = Generators.input(inProd);
const numericas = colunas.filter((c) => c.includes("_mil_") || c.includes("_kg_"));
const inMed = Inputs.select(numericas, {label: "Variável do gráfico", format: (c) => ROTULOS[c] ?? c, value: "producao_mil_t"});
const medida = Generators.input(inMed);
```

```js
const safras = (await db.query(`select distinct ${colSafra} as s from ${T} where produto = ? order by s`, [produto])).map((d) => d.s);
const inSafra = Inputs.select(safras, {label: "Safra", value: safras.includes("UNICA") ? "UNICA" : safras[0]});
const safra = Generators.input(inSafra);
```

```js
const anos = conjunto.tipo === "levantamento"
  ? (await db.query(`select distinct ano_agricola from ${T} where produto = ? and ${colSafra} = ? order by ano_agricola desc`, [produto, safra])).map((d) => d.ano_agricola)
  : [];
const inAno = Inputs.select(anos, {label: "Ano agrícola"});
const anoAgricola = conjunto.tipo === "levantamento" ? Generators.input(inAno) : null;
```

<div class="filtros">${inConj}${inProd}${inSafra}${conjunto.tipo === "levantamento" ? inAno : ""}${inMed}</div>

```js
const linhas = conjunto.tipo === "serie"
  ? [...await db.query(`select * from ${T} where produto = ? and ${colSafra} = ? order by ano_agricola`, [produto, safra])]
  : [...await db.query(`select * from ${T} where produto = ? and ${colSafra} = ? and ano_agricola = ? order by id_levantamento`, [produto, safra, anoAgricola])];
const eixoX = conjunto.tipo === "serie" ? "ano_agricola" : "dsc_levantamento";
const colunasCSV = colunas.map((c) => ({campo: c, titulo: ROTULOS[c] ?? c}));
const nomeBase = `conab_${slug(conjunto.nome)}_${slug(produto)}_${slug(safra)}${anoAgricola ? "_" + slug(anoAgricola) : ""}`;
```

<div class="card">
  <h2>${produto}, ${safra === "UNICA" ? "safra única" : safra.toLowerCase()}${anoAgricola ? `, ${anoAgricola}` : ""}</h2>
  <p class="fonte">${ROTULOS[medida] ?? medida}, Mato Grosso do Sul.</p>
  ${linhas.length ? resize((w) => Plot.plot({
    width: w, height: 300, marginLeft: 64, marginBottom: 48,
    x: {label: null, type: "band", tickRotate: linhas.length > 20 ? -45 : 0},
    y: {label: ROTULOS[medida] ?? medida, grid: true, tickFormat: (v) => fmt(v)},
    marks: [
      Plot.barY(linhas, {x: eixoX, y: medida, fill: "#004f9f", sort: null, tip: {format: {y: (v) => fmt(v)}}}),
      Plot.ruleY([0])
    ]
  })) : html`<p class="nota">Sem registros para a seleção.</p>`}
</div>

<div class="card">
  <h2>Tabela (${linhas.length} linhas)</h2>
  ${Inputs.table(linhas, {columns: colunas, header: ROTULOS, format: Object.fromEntries(numericas.map((c) => [c, (v) => fmt(v)])), rows: 16, layout: "auto"})}
  <div class="botoes">${botao("Baixar esta tabela (CSV)", () => baixarCSV(linhas, colunasCSV, `${nomeBase}.csv`))}${botao("Baixar o conjunto completo (CSV)", async () => baixarCSV([...await db.query(`select * from ${T} order by produto, ano_agricola`)], colunasCSV, `conab_${slug(conjunto.nome)}_completo.csv`))}</div>
</div>

<p class="fonte">Fonte: CONAB, Portal de Informações Agropecuárias (arquivos de dados de safra), filtrados para MS. Área em mil hectares, produção em mil toneladas, produtividade em toneladas por hectare.</p>
