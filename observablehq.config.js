// Configuração do site (Observable Framework)
export default {
  title: "Painel Agropecuário de MS",
  root: "src",
  output: "dist",
  pages: [
    {name: "Lavouras", path: "/lavouras"},
    {name: "Pecuária", path: "/pecuaria"},
    {name: "Florestas plantadas", path: "/florestas"},
    {name: "Safra de grãos e cana (CONAB)", path: "/conab"},
    {name: "Estimativa da safra (LSPA)", path: "/lspa"},
    {name: "Downloads e fontes", path: "/dados"}
  ],
  style: "estilo.css",
  head: `<link rel="icon" href="data:,">`,
  header: `<div class="gov-faixa"><span class="gov-faixa__gov">Governo de Mato Grosso do Sul</span><span class="gov-faixa__sep">|</span><span>SEMADESC</span></div>`,
  footer: `SEMADESC, Secretaria de Estado de Meio Ambiente, Desenvolvimento, Ciência, Tecnologia e Inovação. Dados públicos das fontes indicadas em cada página.`,
  sidebar: true,
  toc: false,
  pager: false,
  search: false,
  cleanUrls: true
};
