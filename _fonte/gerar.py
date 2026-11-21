#!/usr/bin/env python3
"""Gera o site estático Serras e Formas a partir de _fonte/*.json.
Uso (na raiz do repositório): python3 _fonte/gerar.py [--dominio https://www.serraseformas.com.br]
As páginas são escritas na raiz do repositório; a pasta media/ é mantida como está."""
import json, re, sys, os, shutil, html, math, unicodedata
from urllib.parse import quote_plus

args = sys.argv[1:]
FONTE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(FONTE)
SEM_VIDEOS = "--sem-videos" in args
DOM = args[args.index("--dominio") + 1] if "--dominio" in args else "https://www.serraseformas.com.br"
ler = lambda n: json.load(open(os.path.join(FONTE, n + ".json"), encoding="utf-8"))
A = sorted(ler("artigos"), key=lambda a: a["data"], reverse=True)  # sort estável: mantém a ordem do arquivo nos empates
R, F = ler("referencias"), ler("fotos")

SECOES = [
 ("afiacao","Afiação","Pedras, ângulos e métodos para um fio que corta sem esforço."),
 ("ferramentas","Ferramentas manuais","Uma a uma: anatomia, escolha, uso e cuidado de cada ferramenta."),
 ("maquinas","Máquinas","Regulagem, manutenção e segurança das máquinas estacionárias."),
 ("encaixes","Técnicas e encaixes","Espiga e furo, rabo de andorinha, sashimono e outras uniões."),
 ("madeiras","Madeiras","Espécies brasileiras e estrangeiras, secagem e madeira de demolição."),
 ("acabamento","Acabamento","Lixas, óleos, ceras e vernizes."),
 ("oficina","Oficina","Bancadas, gabaritos, acessórios e máquinas feitas em casa."),
 ("projetos","Projetos","Peças construídas e projetos em andamento, com medidas."),
 ("traducoes","Traduções","Artigos clássicos e atuais vertidos do inglês para o português."),
 ("formacao","Formação","Escolas, cursos e mestres no Brasil e no mundo."),
 ("cronicas","Crônicas","Histórias de oficina."),
]
SEC = {s[0]: s for s in SECOES}
MESES = "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()
e = lambda s: html.escape(str(s), quote=True)
sem_tags = lambda h: re.sub(r"<[^>]+>", " ", h)
def minutos(a): return max(1, round(len(sem_tags(a["corpo"]).split()) / 200))
def data_br(s): y, m, dd = map(int, s.split("-")); return f"{dd} de {MESES[m-1]} de {y}"
def plural(n, s, p): return f"{n} {s if n == 1 else p}"
def conta(sid): return sum(1 for a in A if a["secao"] == sid)
def pag_artigo(a): return f"artigo-{a['slug']}.html"
def pag_secao(sid): return f"secao-{sid}.html"
def norm(s): return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()

# ---- CSS e símbolos tirados da versão de uma página ----
src = open(os.path.join(FONTE, "modelo.html"), encoding="utf-8").read()
css = src[src.index("<style>") + 7: src.index("</style>")]
css += "\n.lista a{color:inherit}.sr{position:absolute;left:-9999px}\n.corpo figure.so-capa{position:relative}.corpo figure.so-capa a{color:var(--mata)}\n"
simbolos = src[src.index('<svg width="0" height="0"'): src.index("</svg>", src.index('<svg width="0" height="0"')) + 6]
painel = src[src.index('<svg class="panorama"'): src.index("</svg>", src.index('<svg class="panorama"')) + 6]
stack_js = src[src.index("<script>new MutationObserver"): src.index("</script>", src.index("<script>new MutationObserver")) + 9]

def pagina(nome, titulo, descricao, corpo, ativo=""):
    def item(href, rot, k):
        cur = ' aria-current="page"' if k == ativo else ""
        return f'<a href="{href}"{cur}>{rot}</a>'
    nav = item("index.html","Início","inicio") + item("biblioteca.html","Biblioteca","biblioteca") + item("referencias.html","Referências","referencias") + item("galeria.html","Galeria","galeria")
    url = DOM.rstrip("/") + "/" + ("" if nome == "index.html" else nome)
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Serras e Formas">
<meta property="og:title" content="{e(titulo)}"><meta property="og:description" content="{e(descricao)}">
<meta property="og:locale" content="pt_BR">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
{stack_js}
</head>
<body>
{simbolos}
<header class="top"><div class="wrap">
<a class="marca" href="index.html" aria-label="Serras e Formas, página inicial"><svg aria-hidden="true"><use href="#logo"/></svg>Serras e Formas</a>
<nav class="menu" aria-label="Principal">{nav}</nav>
</div></header>
<main id="app">
{corpo}
</main>
<footer><div class="wrap"><span><b>Serras e Formas</b> · Biblioteca de marcenaria em língua portuguesa · Serra Fluminense, RJ</span><span>{plural(len(A),"artigo","artigos")} no acervo</span></div></footer>
</body>
</html>
"""

def item_lista(a):
    s = SEC[a["secao"]][1]
    return f'<li data-s="{a["secao"]}"><a href="{pag_artigo(a)}"><h3>{e(a["titulo"])}</h3><p>{e(a["resumo"])}</p><span class="meta"><b>{e(s)}</b>{e(a["tipo"])} · {minutos(a)} min</span></a></li>'

def link_ref(it): return it.get("u") or ("https://www.youtube.com/results?search_query=" + quote_plus(it["yt"]))
def onde(it):
    if not it.get("u"): return "Abrir no YouTube"
    return re.sub(r"^https?://(www\.)?", "", it["u"]).rstrip("/").split("/")[0]

def ajusta_corpo(h):
    """Troca vídeos por capa clicável na versão sem vídeos e marca as tabelas para o celular."""
    if SEM_VIDEOS:
        def troca(m):
            poster = re.search(r'poster="([^"]+)"', m.group(0)).group(1)
            return f'<img src="{poster}" alt="Quadro do vídeo" loading="lazy">'
        h = re.sub(r"<video[^>]*></video>", troca, h)
        h = h.replace("<figcaption>Vídeo da oficina:", "<figcaption>Vídeo da oficina (em breve no canal):")
    return h

os.makedirs(OUT, exist_ok=True)
w = lambda nome, txt: open(os.path.join(OUT, nome), "w", encoding="utf-8").write(txt)
w("style.css", css)
w("favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 22"><path d="M1 20 L7 6 L10 20 L14 9 L17 20 L21 11 L24 20 Z" fill="#1d5a3b"/><circle cx="24" cy="5" r="3.6" fill="#f0b400"/></svg>')

# ---- início ----
grade = "".join(f'<a href="{pag_secao(sid)}"><h3>{nome}<span>{conta(sid) or "em breve"}</span></h3><p>{desc}</p></a>' for sid, nome, desc in SECOES)
grade += f'<a href="referencias.html"><h3>Referências<span>{sum(len(p["itens"]) for p in R)}</span></h3><p>Mestres, canais, revistas e escolas do mundo todo.</p></a>'
inicio = f"""<section class="hero">
<div class="wrap"><h1>Serras e Formas</h1><p class="sub">Biblioteca de marcenaria em língua portuguesa. Afiação, ferramentas, máquinas, encaixes e madeiras, estudados um a um.</p></div>
{painel}
<form class="busca" role="search" action="biblioteca.html" method="get">
<svg aria-hidden="true"><use href="#lupa"/></svg><label class="sr" for="q-inicio">Buscar no acervo</label>
<input id="q-inicio" name="q" type="search" placeholder="Buscar: afiação, serra de fita, encaixe…" autocomplete="off">
</form></section>
<section class="band"><div class="wrap"><div class="titulo-bloco"><h2>Seções</h2><a href="biblioteca.html">Ver o acervo inteiro</a></div><div class="grade">{grade}</div></div></section>
<section class="band" style="padding-top:0"><div class="wrap"><div class="titulo-bloco"><h2>Publicados recentemente</h2><a href="biblioteca.html">Todos os artigos</a></div>
<ul class="lista">{"".join(item_lista(a) for a in A[:6])}</ul></div></section>
<section class="band faixa"><div class="wrap"><div class="titulo-bloco"><h2>Referências pelo mundo</h2><a href="referencias.html">Abrir o índice</a></div>
<p>Mestres, canais, revistas, escolas e bancos de dados do Brasil, dos Estados Unidos, da Inglaterra e de outros países, reunidos num só lugar e comentados em português.</p>
<div class="paises">{"".join(f'<a href="referencias.html#pais-{p["id"]}">{p["pais"]}</a>' for p in R)}</div></div></section>
<section class="band"><div class="wrap manifesto"><h2>Por que uma biblioteca</h2><div>
<p>Quase tudo o que se escreve de melhor sobre marcenaria está em inglês, em francês, em alemão ou em japonês. Serras e Formas reúne, traduz e organiza esse conhecimento em português, um tema por vez.</p>
<p>Cada estudo da oficina vira um artigo: a regulagem de uma máquina, uma ferramenta manual vista por dentro, um encaixe, uma madeira. Nada se perde no celular. Tudo fica aqui, com as fontes indicadas.</p></div></div></section>"""
w("index.html", pagina("index.html", "Serras e Formas — biblioteca de marcenaria em português",
  "Biblioteca de marcenaria em língua portuguesa: afiação, ferramentas manuais, máquinas, encaixes, madeiras, oficina e referências do mundo todo.", inicio, "inicio"))

# ---- biblioteca (lista completa + busca no navegador) ----
indice = [{"s": a["secao"], "t": norm(a["titulo"] + " " + a["resumo"] + " " + sem_tags(a["corpo"]))} for a in A]
chips = '<button type="button" data-s="" aria-pressed="true">Todas</button>' + "".join(f'<button type="button" data-s="{sid}" aria-pressed="false">{nome}</button>' for sid, nome, _ in SECOES if conta(sid))
bib = f"""<div class="wrap">
<div class="cabeca"><h1>Biblioteca</h1><p>Todo o acervo, do mais recente ao mais antigo. Busque por palavra ou filtre por seção.</p></div>
<div class="filtro"><svg aria-hidden="true"><use href="#lupa"/></svg><label class="sr" for="q">Buscar no acervo</label><input id="q" type="search" placeholder="Buscar no acervo" autocomplete="off"></div>
<div class="chips" role="group" aria-label="Filtrar por seção" id="chips" style="margin-top:14px">{chips}</div>
<p class="contagem" id="cont" aria-live="polite">{plural(len(A),"artigo","artigos")}</p>
<ul class="lista" id="todos">{"".join(item_lista(a) for a in A)}</ul>
<p class="vazio" id="vazio" hidden>Nada encontrado. Tente outra palavra, como “plaina” ou “madeira”.</p>
</div>
<script>
{{
const I = {json.dumps(indice, ensure_ascii=False)};
const q = document.getElementById("q"), lis = [...document.querySelectorAll("#todos li")], chips = document.getElementById("chips");
let sec = "";
const norm = s => s.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase();
function desenha() {{
  const t = norm(q.value.trim()); let n = 0;
  lis.forEach((li, i) => {{ const ok = (!sec || I[i].s === sec) && (!t || I[i].t.includes(t)); li.hidden = !ok; if (ok) n++; }});
  document.getElementById("cont").textContent = n + (n === 1 ? " artigo" : " artigos") + (t ? " para “" + q.value.trim() + "”" : "");
  document.getElementById("vazio").hidden = n > 0;
}}
chips.addEventListener("click", ev => {{ const b = ev.target.closest("button"); if (!b) return; sec = b.dataset.s; chips.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x === b)); desenha(); }});
q.addEventListener("input", desenha);
const p = new URLSearchParams(location.search).get("q"); if (p) {{ q.value = p; desenha(); }}
}}
</script>"""
w("biblioteca.html", pagina("biblioteca.html", "Biblioteca — Serras e Formas", "Todos os artigos de marcenaria do acervo Serras e Formas, com busca e filtro por seção.", bib, "biblioteca"))

# ---- seções ----
for sid, nome, desc in SECOES:
    lista = [a for a in A if a["secao"] == sid]
    corpo = f'<div class="wrap"><div class="cabeca"><div class="trilha"><a href="biblioteca.html">Biblioteca</a> / Seção</div><h1>{nome}</h1><p>{desc}</p></div>'
    corpo += (f'<p class="contagem">{plural(len(lista),"artigo","artigos")}</p><ul class="lista">{"".join(item_lista(a) for a in lista)}</ul>' if lista
              else '<div class="vazio">Esta seção ainda não tem artigos. Os primeiros chegam em breve.</div>') + "</div>"
    w(pag_secao(sid), pagina(pag_secao(sid), f"{nome} — Serras e Formas", f"{nome}: {desc}", corpo, "biblioteca"))

# ---- artigos ----
for a in A:
    s = SEC[a["secao"]]
    irm = [x for x in A if x["secao"] == a["secao"]]
    i = irm.index(a); ant = irm[i+1] if i + 1 < len(irm) else None; prox = irm[i-1] if i > 0 else None
    fontes = ""
    if a.get("fontes"):
        fontes = '<div class="fontes"><h3>Fontes e leitura complementar</h3><ul>' + "".join(f'<li><a href="{e(f["u"])}" target="_blank" rel="noopener">{e(f["t"])}</a></li>' for f in a["fontes"]) + "</ul></div>"
    viz = ""
    if ant or prox:
        viz = '<nav class="vizinhos" aria-label="Outros artigos da seção">'
        if ant: viz += f'<a href="{pag_artigo(ant)}"><small>Anterior</small>{e(ant["titulo"])}</a>'
        if prox: viz += f'<a class="prox" href="{pag_artigo(prox)}"><small>Próximo</small>{e(prox["titulo"])}</a>'
        viz += "</nav>"
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["titulo"], "description": a["resumo"],
          "datePublished": a["data"], "inLanguage": "pt-BR", "publisher": {"@type": "Organization", "name": "Serras e Formas"}}
    corpo = f"""<div class="wrap"><article class="texto">
<div class="cabeca" style="border:0;margin:0;padding-bottom:0"><div class="trilha"><a href="biblioteca.html">Biblioteca</a> / <a href="{pag_secao(s[0])}">{s[1]}</a></div>
<h1>{e(a["titulo"])}</h1>
<div class="linha-meta"><span><b>{e(a["tipo"])}</b></span><span>{data_br(a["data"])}</span><span>{minutos(a)} min de leitura</span></div></div>
<p class="lead" style="margin-top:22px">{e(a["resumo"])}</p>
<div class="corpo">{ajusta_corpo(a["corpo"])}</div>
{fontes}{viz}
</article></div>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>"""
    w(pag_artigo(a), pagina(pag_artigo(a), f"{a['titulo']} — Serras e Formas", a["resumo"], corpo, "biblioteca"))

# ---- referências ----
total = sum(len(p["itens"]) for p in R)
refs = f'<div class="wrap"><div class="cabeca"><h1>Referências</h1><p>{total} mestres, canais, revistas, escolas e bancos de dados de {len(R)} países, comentados em português.</p></div>'
refs += '<div class="paises claro" style="margin-bottom:32px">' + "".join(f'<a href="#pais-{p["id"]}">{p["pais"]}</a>' for p in R) + "</div>"
for p in R:
    refs += f'<section class="ref-grupo" id="pais-{p["id"]}"><h2>{p["pais"]}<span>{plural(len(p["itens"]),"referência","referências")}</span></h2><div class="refs">'
    refs += "".join(f'<a href="{e(link_ref(it))}" target="_blank" rel="noopener"><span class="tipo">{e(it["tipo"])}</span><strong>{e(it["n"])}</strong><p>{e(it["d"])}</p><em>{e(onde(it))}</em></a>' for it in p["itens"])
    refs += "</div></section>"
refs += "</div>"
w("referencias.html", pagina("referencias.html", "Referências de marcenaria pelo mundo — Serras e Formas",
  "Mestres, canais de YouTube, revistas, escolas e bancos de dados de marcenaria do Brasil, EUA, Inglaterra, Japão, França e outros países.", refs, "referencias"))

# ---- galeria ----
gal = '<div class="wrap"><div class="cabeca"><h1>Galeria</h1><p>A oficina, as ferramentas e algumas peças. Toque numa foto para abrir o artigo relacionado.</p></div><div class="fotos">'
gal += "".join(f'<a class="foto" href="{(f["link"].replace("artigo-", "artigo-", 1) + ".html") if f.get("link") else "galeria.html"}"><img src="{e(f["src"])}" alt="{e(f["alt"])}" loading="lazy"><span>{e(f.get("legenda",""))}</span></a>' for f in F)
gal += "</div></div>"
w("galeria.html", pagina("galeria.html", "Galeria — Serras e Formas", "Fotos da oficina, das máquinas e das peças do Serras e Formas.", gal, "galeria"))

# ---- 404, robots e sitemap ----
w("404.html", pagina("404.html", "Página não encontrada — Serras e Formas", "Página não encontrada.",
  '<div class="wrap"><div class="cabeca"><h1>Página não encontrada</h1><p>O endereço pode ter mudado. <a href="biblioteca.html" style="color:var(--mata)">Voltar à biblioteca</a>.</p></div></div>'))
paginas = ["", "biblioteca.html", "referencias.html", "galeria.html"] + [pag_secao(s[0]) for s in SECOES] + [pag_artigo(a) for a in A]
base = DOM.rstrip("/") + "/"
w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
  "".join(f"  <url><loc>{base}{p}</loc></url>\n" for p in paginas) + "</urlset>\n")
w("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {base}sitemap.xml\n")

print("ok", len(os.listdir(OUT)), "arquivos na raiz")
