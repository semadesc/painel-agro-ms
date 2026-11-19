// Funções comuns: formatação, mapa municipal e downloads.
import * as Plot from "npm:@observablehq/plot";

export const nf = new Intl.NumberFormat("pt-BR", {maximumFractionDigits: 2});
export const fmt = (v) => (v == null || Number.isNaN(v) ? "" : nf.format(v));

// Rampa sequencial em verde, do manual de identidade visual (claro para escuro)
export const RAMPA = ["#e6f4eb", "#b7e0c4", "#7cc69a", "#36a865", "#009e3d", "#006b2d"];
export const AZUL = "#004f9f";
export const VERDE = "#009e3d";

// Mapa coroplético dos municípios. linhas: [{cod_ibge, localidade, valor, valor_num, unidade}]
export function mapaMunicipal(geo, linhas, {width = 640, titulo = "", unidade = ""} = {}) {
  const porCod = new Map(linhas.map((d) => [String(d.cod_ibge), d]));
  const feats = geo.features.map((f) => {
    const d = porCod.get(String(f.properties.id));
    return {...f, properties: {...f.properties, linha: d, v: d?.valor_num ?? null, bruto: d?.valor ?? null}};
  });
  const comValor = feats.filter((f) => f.properties.v != null);
  const semValor = feats.filter((f) => f.properties.v == null);
  const fc = (fs) => ({type: "FeatureCollection", features: fs});
  const temDados = comValor.length > 0;
  return Plot.plot({
    width,
    height: Math.round(width * 0.95),
    projection: {type: "mercator", domain: geo},
    title: titulo,
    color: temDados
      ? {type: "quantile", n: Math.min(6, new Set(comValor.map((f) => f.properties.v)).size), range: RAMPA, legend: true,
         label: unidade, tickFormat: (v) => nf.format(v), style: {fontSize: "12px"}}
      : undefined,
    marks: [
      Plot.geo(fc(semValor), {fill: "#f1f1f2", stroke: "#fff", strokeWidth: 0.8,
        title: (f) => `${f.properties.name}\n${f.properties.bruto === "X" ? "valor sob sigilo (X)" : "sem registro"}`}),
      temDados ? Plot.geo(fc(comValor), {fill: (f) => f.properties.v, stroke: "#fff", strokeWidth: 0.8,
        title: (f) => `${f.properties.name}\n${nf.format(f.properties.v)} ${unidade}`, tip: true}) : null,
      Plot.geo(geo, {stroke: "#9a9a9a", strokeWidth: 0.2})
    ]
  });
}

// ---- downloads ----
function salvar(blob, nome) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = nome;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

// CSV com separador ";" e vírgula decimal, que o Excel em português abre direto.
export function baixarCSV(linhas, colunas, nome) {
  const cel = (v) => {
    if (v == null) return "";
    if (typeof v === "number") return String(v).replace(".", ",");
    const s = String(v);
    return /[;"\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const txt = [colunas.map((c) => c.titulo).join(";")]
    .concat(linhas.map((l) => colunas.map((c) => cel(l[c.campo])).join(";")))
    .join("\r\n");
  salvar(new Blob(["﻿" + txt], {type: "text/csv;charset=utf-8"}), nome);
}

function svgDe(figura) {
  return figura.tagName.toLowerCase() === "svg" ? figura : figura.querySelector("svg:not(.plot-swatch svg)") ?? figura.querySelector("svg");
}

export function baixarSVG(figura, nome) {
  const svg = svgDe(figura).cloneNode(true);
  svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  salvar(new Blob([new XMLSerializer().serializeToString(svg)], {type: "image/svg+xml"}), nome);
}

// PNG da figura inteira (mapa + legenda), em resolução dobrada
export async function baixarPNG(figura, nome) {
  const svgs = [...figura.querySelectorAll("svg")];
  const caixa = figura.getBoundingClientRect();
  const escala = 2;
  const canvas = document.createElement("canvas");
  canvas.width = caixa.width * escala;
  canvas.height = caixa.height * escala;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  for (const s of svgs) {
    const r = s.getBoundingClientRect();
    const c = s.cloneNode(true);
    c.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    c.setAttribute("width", r.width);
    c.setAttribute("height", r.height);
    const url = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(c)], {type: "image/svg+xml"}));
    const img = new Image();
    await new Promise((ok, erro) => { img.onload = ok; img.onerror = erro; img.src = url; });
    ctx.drawImage(img, (r.left - caixa.left) * escala, (r.top - caixa.top) * escala, r.width * escala, r.height * escala);
    URL.revokeObjectURL(url);
  }
  canvas.toBlob((b) => salvar(b, nome), "image/png");
}

export function botao(texto, acao) {
  const b = document.createElement("button");
  b.type = "button";
  b.textContent = texto;
  b.onclick = acao;
  return b;
}

export const slug = (s) => String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^A-Za-z0-9]+/g, "_").replace(/^_|_$/g, "").toLowerCase();
