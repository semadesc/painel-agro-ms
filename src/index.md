---
title: Início
toc: false
---

# Painel Agropecuário de Mato Grosso do Sul

<p class="nota">Dados oficiais da produção agropecuária de Mato Grosso do Sul, por município e por safra, reunidos a partir do IBGE e da CONAB. Consulte por produto, ano e município, veja tabelas e mapas e baixe os arquivos. Os dados são apresentados como as fontes publicam, sem tratamento.</p>

```js
const atualizacao = FileAttachment("data/atualizacao.json").json();
```

<div class="temas">
  <a href="./lavouras"><strong>Lavouras</strong><span>Área, produção, rendimento e valor por produto e município (IBGE, PAM, desde 1974)</span></a>
  <a href="./pecuaria"><strong>Pecuária</strong><span>Rebanhos e produção de origem animal por município (IBGE, PPM, desde 1974)</span></a>
  <a href="./florestas"><strong>Florestas plantadas</strong><span>Área por espécie e produção da silvicultura por município (IBGE, PEVS)</span></a>
  <a href="./conab"><strong>Safra de grãos e cana</strong><span>Série histórica e levantamentos mensais da CONAB para MS</span></a>
  <a href="./lspa"><strong>Estimativa da safra</strong><span>Estimativas mensais do IBGE para a safra do ano (LSPA)</span></a>
  <a href="./dados"><strong>Downloads e fontes</strong><span>Arquivos completos, fontes e calendário de atualização</span></a>
</div>

## Atualização

<p class="nota">Os dados são coletados automaticamente toda segunda-feira. Última montagem do site: <strong>${atualizacao.gerado_em}</strong>. Períodos mais recentes disponíveis: PAM ${atualizacao.pam}, PPM ${atualizacao.ppm}, PEVS ${atualizacao.pevs} e LSPA ${atualizacao.lspa.slice(4)}/${atualizacao.lspa.slice(0, 4)}.</p>
