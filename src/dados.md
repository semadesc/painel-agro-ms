---
title: Downloads e fontes
---

# Downloads e fontes

<p class="nota">Cada conjunto pode ser baixado completo. O arquivo Parquet abre no Python, no R, no QGIS e no Power BI; o CSV abre no Excel. Os arquivos originais da coleta, um por ano, ficam no repositório público do projeto.</p>

```js
import {baixarCSV, botao} from "./components/util.js";
const REPO = "https://github.com/semadesc/painel-agro-ms/tree/main/data";
const CONJ = [
  {nome: "Lavouras temporárias e permanentes", fonte: "IBGE, PAM", tabela: "SIDRA 5457", recorte: "Município, anual, desde 1974", arq: FileAttachment("data/pam.parquet"), pasta: "ibge/pam/lavouras"},
  {nome: "Efetivo dos rebanhos", fonte: "IBGE, PPM", tabela: "SIDRA 3939", recorte: "Município, anual, desde 1974", arq: FileAttachment("data/ppm_rebanhos.parquet"), pasta: "ibge/ppm/rebanhos"},
  {nome: "Produção de origem animal", fonte: "IBGE, PPM", tabela: "SIDRA 74", recorte: "Município, anual, desde 1974", arq: FileAttachment("data/ppm_origem_animal.parquet"), pasta: "ibge/ppm/producao_origem_animal"},
  {nome: "Área de florestas plantadas", fonte: "IBGE, PEVS", tabela: "SIDRA 5930", recorte: "Município, anual, desde 2013", arq: FileAttachment("data/pevs_area.parquet"), pasta: "ibge/pevs/area_silvicultura"},
  {nome: "Produção da silvicultura", fonte: "IBGE, PEVS", tabela: "SIDRA 291", recorte: "Município, anual, desde 1986", arq: FileAttachment("data/pevs_producao.parquet"), pasta: "ibge/pevs/producao_silvicultura"},
  {nome: "Estimativa mensal da safra", fonte: "IBGE, LSPA", tabela: "SIDRA 6588", recorte: "Estado, mensal, desde 2006", arq: FileAttachment("data/lspa.parquet"), pasta: "ibge/lspa/estimativa_safra"},
  {nome: "Grãos: série histórica", fonte: "CONAB", tabela: "SerieHistoricaGraos", recorte: "Estado, por safra, desde 1976/77", arq: FileAttachment("data/conab_serie_historica_graos.parquet"), pasta: "conab"},
  {nome: "Grãos: levantamentos", fonte: "CONAB", tabela: "LevantamentoGraos", recorte: "Estado, por levantamento mensal", arq: FileAttachment("data/conab_levantamento_graos.parquet"), pasta: "conab"},
  {nome: "Cana-de-açúcar: série histórica", fonte: "CONAB", tabela: "SerieHistoricaCana", recorte: "Estado, por safra", arq: FileAttachment("data/conab_serie_historica_cana.parquet"), pasta: "conab"},
  {nome: "Cana-de-açúcar: levantamentos", fonte: "CONAB", tabela: "LevantamentoCana", recorte: "Estado, por levantamento", arq: FileAttachment("data/conab_levantamento_cana.parquet"), pasta: "conab"}
];

async function csvCompleto(c) {
  const t = await c.arq.parquet();
  const linhas = t.toArray().map((r) => r.toJSON());
  const colunas = t.schema.fields.map((f) => ({campo: f.name, titulo: f.name}));
  baixarCSV(linhas, colunas, c.arq.name.replace(".parquet", ".csv"));
}
```

<div class="card">

```js
display(html`<table class="tabela-dados">
  <thead><tr><th>Conjunto</th><th>Fonte</th><th>Tabela</th><th>Recorte</th><th>Baixar</th></tr></thead>
  <tbody>${CONJ.map((c) => html`<tr>
    <td>${c.nome}</td><td>${c.fonte}</td><td>${c.tabela}</td><td>${c.recorte}</td>
    <td><div class="botoes">${botao("CSV", () => csvCompleto(c))}<a href="${c.arq.href}" download><button type="button">Parquet</button></a><a href="${REPO}/${c.pasta}" target="_blank" rel="noopener"><button type="button">Originais</button></a></div></td>
  </tr>`)}</tbody>
</table>`);
```

</div>

## Fontes

- **IBGE**, Sistema IBGE de Recuperação Automática (SIDRA), API de agregados: PAM, PPM, PEVS e LSPA.
- **CONAB**, Portal de Informações Agropecuárias, arquivos de dados de safra de grãos e de cana-de-açúcar.
- Malha municipal: IBGE.

## Como os dados são tratados

- Os valores são mantidos como a fonte publica. "X" indica valor sob sigilo do IBGE.
- Nas tabelas do IBGE, células vazias e zeros não são armazenados: a ausência de registro equivale a zero.
- Valores monetários antigos estão na moeda corrente de cada ano (ver a coluna de unidade).
- A coleta é automática, toda segunda-feira; o código está no [repositório do projeto](https://github.com/semadesc/painel-agro-ms).
