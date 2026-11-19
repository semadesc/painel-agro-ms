---
title: Estimativa da safra (LSPA)
---

# Estimativa da safra (LSPA)

<p class="nota">Levantamento Sistemático da Produção Agrícola do IBGE: estimativas mensais da safra do ano para Mato Grosso do Sul. Cada mês, o IBGE revisa a estimativa do ano. Dados como publicados, sem tratamento.</p>

```js
import {baixarCSV, botao, fmt, slug} from "./components/util.js";
const db = await DuckDBClient.of({lspa: FileAttachment("data/lspa.parquet")});
const produtos = (await db.query(`select distinct categoria from lspa order by categoria`)).map((d) => d.categoria);
const variaveis = (await db.query(`select distinct variavel from lspa order by variavel`)).map((d) => d.variavel);
const inProd = Inputs.select(produtos, {label: "Produto", value: produtos.includes("1.17 Soja") ? "1.17 Soja" : produtos[0]});
const inVar = Inputs.select(variaveis, {label: "Variável", value: variaveis.includes("Produção") ? "Produção" : variaveis[0]});
const produto = Generators.input(inProd);
const variavel = Generators.input(inVar);
const MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
const rotuloMes = (p) => `${MESES[Number(String(p).slice(4, 6)) - 1]}/${String(p).slice(0, 4)}`;
```

```js
const anos = [...new Set((await db.query(`select distinct periodo from lspa where categoria = ? and variavel = ? order by periodo desc`, [produto, variavel])).map((d) => String(d.periodo).slice(0, 4)))];
const inAno = Inputs.select(anos, {label: "Ano da safra"});
const ano = Generators.input(inAno);
```

<div class="filtros">${inProd}${inVar}${inAno}</div>

```js
const linhas = [...await db.query(`select periodo, localidade, variavel, categoria, valor, valor_num, unidade from lspa where categoria = ? and variavel = ? and periodo like ? order by periodo`, [produto, variavel, `${ano}%`])]
  .map((d) => ({...d, mes: rotuloMes(d.periodo)}));
const unidade = linhas[0]?.unidade ?? "";
const colunasCSV = [
  {campo: "periodo", titulo: "Mês de referência (AAAAMM)"}, {campo: "localidade", titulo: "UF"}, {campo: "categoria", titulo: "Produto"},
  {campo: "variavel", titulo: "Variável"}, {campo: "valor", titulo: "Valor"}, {campo: "unidade", titulo: "Unidade"}
];
const nomeBase = `lspa_${slug(produto)}_${slug(variavel)}`;
```

<div class="card">
  <h2>${produto}: estimativas de ${ano}</h2>
  <p class="fonte">${variavel}${unidade ? ` (${unidade})` : ""}, Mato Grosso do Sul, por mês de divulgação.</p>
  ${linhas.length ? resize((w) => Plot.plot({
    width: w, height: 300, marginLeft: 80,
    x: {label: null, type: "band", domain: linhas.map((d) => d.mes)},
    y: {label: unidade, grid: true, tickFormat: (v) => fmt(v)},
    marks: [
      Plot.barY(linhas.filter((d) => d.valor_num != null), {x: "mes", y: "valor_num", fill: "#004f9f", tip: {format: {y: (v) => fmt(v)}}}),
      Plot.ruleY([0])
    ]
  })) : html`<p class="nota">Sem registros para a seleção.</p>`}
</div>

<div class="card">
  <h2>Tabela</h2>
  ${Inputs.table(linhas, {columns: ["mes", "valor_num", "unidade"], header: {mes: "Mês de referência", valor_num: "Valor", unidade: "Unidade"}, format: {valor_num: (v, i, d) => (v == null ? d[i].valor : fmt(v))}, rows: 13, layout: "auto"})}
  <div class="botoes">${botao("Baixar esta tabela (CSV)", () => baixarCSV(linhas, colunasCSV, `${nomeBase}_${ano}.csv`))}${botao("Baixar todos os anos (CSV)", async () => baixarCSV([...await db.query(`select * from lspa where categoria = ? and variavel = ? order by periodo`, [produto, variavel])], colunasCSV, `${nomeBase}_todos.csv`))}</div>
</div>

<p class="fonte">Fonte: IBGE, Levantamento Sistemático da Produção Agrícola (LSPA), tabela SIDRA 6588.</p>
