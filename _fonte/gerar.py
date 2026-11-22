#!/usr/bin/env python3
"""Gera o site estático Serras & Formas a partir de _fonte/*.json.
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
 ("historia","História","A origem das ferramentas, dos fabricantes e dos ofícios."),
 ("glossario","Glossário","Vocabulário da marcenaria em português e inglês."),
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

# ---- estilo, símbolos e script das tabelas ----
css = open(os.path.join(FONTE, "estilo.css"), encoding="utf-8").read()
css += "\n.lista a{color:inherit}.sr{position:absolute;left:-9999px}\n"
simbolos = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="lupa" viewBox="0 0 20 20"><circle cx="8.5" cy="8.5" r="6" fill="none" stroke="currentColor" stroke-width="2"/><path d="M13 13l5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></symbol></svg>'
stack_js = """<script>new MutationObserver(()=>{for(const c of document.querySelectorAll('.stack td:not([data-l])')){let i=0,p=c;while(p=p.previousElementSibling)i+=p.colSpan;c.dataset.l=c.closest('table').rows[0].cells[i]?.textContent||''}}).observe(document,{childList:true,subtree:true})</script>"""
ESCOLAS, PAUTAS = ler("escolas"), ler("pautas")
ASSINATURA = open(os.path.join(FONTE, "assinatura.svg"), encoding="utf-8").read()

def pagina(nome, titulo, descricao, corpo, ativo=""):
    def item(href, rot, k):
        cur = ' aria-current="page"' if k == ativo else ""
        return f'<a href="{href}"{cur}>{rot}</a>'
    nav = item("index.html","Início","inicio") + item("biblioteca.html","Biblioteca","biblioteca") + item("index.html#cursos","Onde aprender","cursos") + item("referencias.html","Referências","referencias") + item("galeria.html","Galeria","galeria")
    url = DOM.rstrip("/") + "/" + ("" if nome == "index.html" else nome)
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Serras & Formas">
<meta property="og:title" content="{e(titulo)}"><meta property="og:description" content="{e(descricao)}">
<meta property="og:locale" content="pt_BR">
<link rel="icon" href="media/favicon.png" type="image/png">
<link rel="stylesheet" href="style.css">
{stack_js}
</head>
<body>
{simbolos}
<header class="top"><div class="wrap">
<a class="marca" href="index.html" aria-label="Serras &amp; Formas, página inicial"><img src="media/logo-96.png" alt="" width="38" height="38"><span class="tit"><b>Serras <em>&amp;</em> Formas</b><small>Artigos e técnicas de marcenaria</small></span></a>
<nav class="menu" aria-label="Principal">{nav}</nav>
</div></header>
<main id="app">
{corpo}
</main>
<footer><div class="wrap"><div class="rod"><img src="media/logo-96.png" alt="Logotipo Serras &amp; Formas" width="64" height="64"><div><b>Serras &amp; Formas</b><small>Marcenaria • Projetos • Técnicas · Petrópolis, Serra Fluminense</small><small>Um projeto pessoal de compartilhamento de conhecimento, por</small>{ASSINATURA}</div></div><span>{plural(len(A),"artigo","artigos")} no acervo · <a href="index.html#seguranca">Segurança</a></span></div></footer>
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

# ---- início ----
oficina = next((a for a in A if a["slug"] == "como-montar-sua-oficina"), A[0])
grade = "".join(f'<a href="{pag_secao(sid)}"><h3>{nome}<span>{conta(sid) or "em breve"}</span></h3><p>{desc}</p></a>' for sid, nome, desc in SECOES)
grade += f'<a href="referencias.html"><h3>Referências<span>{sum(len(p["itens"]) for p in R)}</span></h3><p>Mestres, canais, revistas e escolas do mundo todo.</p></a>'
cursos = "".join(f'<a href="{e(x["u"]) if x["u"] else "referencias.html#pais-brasil"}"{" target=\"_blank\" rel=\"noopener\"" if x["u"] else ""}><span class="tipo">{e(x["local"])}</span><strong>{e(x["nome"])}</strong><p>{e(x["d"])}</p><em>{"Site e cursos" if x["u"] else "Agenda a confirmar"}</em></a>' for x in ESCOLAS)
pautas = "".join(f'<li><small>{e(x["s"])} · {e(x["st"])}</small><b>{e(x["t"])}</b><span>{e(x["d"])}</span></li>' for x in PAUTAS)
bloco_pautas = (f'<section class="band faixa-clara"><div class="wrap"><span class="eyebrow">Próximos artigos</span><h2>Em preparação</h2><p class="contagem" style="margin-bottom:18px">Pautas planejadas, ainda não publicadas.</p><ul class="pautas">{pautas}</ul></div></section>') if PAUTAS else ""
inicio = f"""<section class="hero"><div class="wrap hero-grid">
<div><span class="eyebrow">Petrópolis · Serra Fluminense</span>
<h1>O prazer de aprender, criar e compartilhar.</h1>
<p class="sub">Guias, ferramentas, projetos e técnicas de marcenaria em português. Um acervo pessoal de descobertas, estudos e experiências que começou em 2020.</p>
<div class="botoes"><a class="btn" href="biblioteca.html">Explorar o acervo</a><a class="btn sec" href="#sobre">Conheça o projeto</a></div>
<form class="busca" role="search" action="biblioteca.html" method="get"><svg aria-hidden="true"><use href="#lupa"/></svg><label class="sr" for="q-inicio">Buscar no acervo</label><input id="q-inicio" name="q" type="search" placeholder="Buscar: afiação, serra de fita, encaixe…" autocomplete="off"></form>
</div>
<figure><img src="media/pedra-itaipava.webp" alt="Vista das montanhas da região de Itaipava a partir de Nogueira, Petrópolis"><figcaption>A paisagem que inspira o Serras &amp; Formas: Nogueira, Petrópolis.</figcaption></figure>
</div></section>

<section class="band" id="sobre"><div class="wrap intro">
<div><span class="eyebrow">Por que este site existe</span><h2>Um caderno aberto de marcenaria</h2>
<p>A marcenaria é um universo de descobertas. Cada ferramenta, cada técnica e cada projeto trazem novas perguntas, e novas oportunidades de aprender.</p>
<p>Comecei a praticar marcenaria em 2020, como hobby. Desde então, venho reunindo experiências em minha pequena oficina nas montanhas de Petrópolis, participando de cursos, estudando ferramentas e consultando livros, artigos e manuais, muitos deles publicados em outros idiomas.</p>
<p>Criei o Serras &amp; Formas para organizar e compartilhar esse material em português. Aqui você encontrará guias práticos, projetos, estudos sobre ferramentas, traduções comentadas, referências técnicas e relatos do que venho aprendendo.</p>
<p>Não sou marceneiro profissional nem professor de marcenaria. Sou um entusiasta que acredita que o conhecimento se torna mais valioso quando é compartilhado.</p>
<div class="assina">{ASSINATURA}<span>Petrópolis, Serra Fluminense</span></div></div>
<aside class="lado"><h3>O que você encontra aqui</h3><ul>
<li><a href="secao-ferramentas.html">Ferramentas</a> e <a href="secao-maquinas.html">máquinas</a>: funcionamento, manutenção e escolha.</li>
<li><a href="secao-encaixes.html">Técnicas</a> e <a href="secao-projetos.html">projetos</a>: exercícios, métodos e experiências.</li>
<li><a href="secao-traducoes.html">Manuais e traduções</a>: referências comentadas em português, com as fontes indicadas.</li>
<li><a href="secao-historia.html">História</a> e <a href="secao-glossario.html">glossário</a>: o contexto e o vocabulário da marcenaria.</li>
<li><a href="#cursos">Formação</a>: onde estudar com quem ensina o ofício.</li>
</ul></aside>
</div></section>

<section class="band" style="padding-top:0"><div class="wrap">
<span class="eyebrow">Primeiro guia publicado</span><h2>Comece pela oficina</h2>
<a class="feature" href="{pag_artigo(oficina)}"><img src="media/oficina-desengrosso-entrada.webp" alt="Desengrosso posicionado sobre a serra de bancada na entrada da oficina" loading="lazy">
<div><span class="eyebrow">Organização do espaço · 17,3 m²</span><h3>Quer montar sua oficina e não sabe por onde começar?</h3>
<p>Uma garagem de 6,40 × 2,70 m serve de estudo de caso para discutir layout, circulação, posição das máquinas, bancada, iluminação, energia, armazenamento e controle de pó. Não é um modelo a copiar: é um ponto de partida para pensar no seu espaço.</p><span class="mais">Ler o guia completo →</span></div></a>
</div></section>

<section class="band faixa-clara"><div class="wrap">
<div class="titulo-bloco"><div><span class="eyebrow">Biblioteca em construção</span><h2>Explore por assunto</h2></div><a href="biblioteca.html">Ver o acervo inteiro</a></div>
<div class="grade">{grade}</div></div></section>

<section class="band"><div class="wrap"><div class="titulo-bloco"><h2>Publicados recentemente</h2><a href="biblioteca.html">Todos os artigos</a></div>
<ul class="lista">{"".join(item_lista(a) for a in A[:6])}</ul></div></section>

{bloco_pautas}

<section class="band" id="cursos"><div class="wrap">
<div class="titulo-bloco"><div><span class="eyebrow">Formação e referências</span><h2>Onde aprender marcenaria</h2></div><a href="referencias.html">Referências pelo mundo</a></div>
<p class="lede" style="max-width:62ch;color:var(--muted);margin:0 0 22px">Minha recomendação mais importante para quem está começando: procure aulas práticas com orientação de profissionais. Estas são referências para explorar; confirme diretamente com cada escola as turmas, os requisitos e a disponibilidade.</p>
<div class="refs">{cursos}</div></div></section>

<section class="band seguranca" id="seguranca"><div class="wrap">
<span class="eyebrow">Antes de começar</span><h2>Segurança em primeiro lugar</h2>
<p>A marcenaria envolve ferramentas cortantes, máquinas de alta rotação, poeira e outros riscos que podem provocar acidentes graves.</p>
<p>Os conteúdos deste site são registros de estudo e experiência pessoal. Não substituem cursos presenciais, treinamento supervisionado, manuais dos fabricantes ou orientações de profissionais qualificados. Cada leitor é responsável por avaliar os riscos e trabalhar dentro dos limites de sua formação e experiência.</p>
<p>Recomendo fortemente fazer cursos de marcenaria antes de operar máquinas, conhecer os procedimentos de segurança de cada equipamento e utilizar os equipamentos de proteção individual adequados à atividade.</p>
<p>Aprender a trabalhar com segurança faz parte da própria arte da marcenaria.</p>
</div></section>"""
w("index.html", pagina("index.html", "Serras & Formas — Artigos e técnicas de marcenaria",
  "Guias, técnicas, projetos, glossário e estudos de marcenaria em português, reunidos por um entusiasta desde 2020, em Petrópolis, Serra Fluminense.", inicio, "inicio"))

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
w("biblioteca.html", pagina("biblioteca.html", "Biblioteca — Serras & Formas", "Todos os artigos de marcenaria do acervo Serras & Formas, com busca e filtro por seção.", bib, "biblioteca"))

# ---- seções ----
for sid, nome, desc in SECOES:
    lista = [a for a in A if a["secao"] == sid]
    corpo = f'<div class="wrap"><div class="cabeca"><div class="trilha"><a href="biblioteca.html">Biblioteca</a> / Seção</div><h1>{nome}</h1><p>{desc}</p></div>'
    corpo += (f'<p class="contagem">{plural(len(lista),"artigo","artigos")}</p><ul class="lista">{"".join(item_lista(a) for a in lista)}</ul>' if lista
              else '<div class="vazio">Esta seção ainda não tem artigos. Os primeiros chegam em breve.</div>') + "</div>"
    w(pag_secao(sid), pagina(pag_secao(sid), f"{nome} — Serras & Formas", f"{nome}: {desc}", corpo, "biblioteca"))

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
          "datePublished": a["data"], "inLanguage": "pt-BR", "publisher": {"@type": "Organization", "name": "Serras & Formas"}}
    corpo = f"""<div class="wrap"><article class="texto">
<div class="cabeca" style="border:0;margin:0;padding-bottom:0"><div class="trilha"><a href="biblioteca.html">Biblioteca</a> / <a href="{pag_secao(s[0])}">{s[1]}</a></div>
<h1>{e(a["titulo"])}</h1>
<div class="linha-meta"><span><b>{e(a["tipo"])}</b></span><span>{data_br(a["data"])}</span><span>{minutos(a)} min de leitura</span></div></div>
<p class="lead" style="margin-top:22px">{e(a["resumo"])}</p>
<div class="corpo">{ajusta_corpo(a["corpo"])}</div>
{fontes}{viz}
</article></div>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>"""
    w(pag_artigo(a), pagina(pag_artigo(a), f"{a['titulo']} — Serras & Formas", a["resumo"], corpo, "biblioteca"))

# ---- referências ----
total = sum(len(p["itens"]) for p in R)
refs = f'<div class="wrap"><div class="cabeca"><h1>Referências</h1><p>{total} mestres, canais, revistas, escolas e bancos de dados de {len(R)} países, comentados em português. Para uma seleção maior, por língua (inglês, francês, espanhol e português), veja <a href="artigo-sites-de-marcenaria-pelo-mundo.html">Sites de marcenaria pelo mundo</a>.</p></div>'
refs += '<div class="paises claro" style="margin-bottom:32px">' + "".join(f'<a href="#pais-{p["id"]}">{p["pais"]}</a>' for p in R) + "</div>"
for p in R:
    refs += f'<section class="ref-grupo" id="pais-{p["id"]}"><h2>{p["pais"]}<span>{plural(len(p["itens"]),"referência","referências")}</span></h2><div class="refs">'
    refs += "".join(f'<a href="{e(link_ref(it))}" target="_blank" rel="noopener"><span class="tipo">{e(it["tipo"])}</span><strong>{e(it["n"])}</strong><p>{e(it["d"])}</p><em>{e(onde(it))}</em></a>' for it in p["itens"])
    refs += "</div></section>"
refs += "</div>"
w("referencias.html", pagina("referencias.html", "Referências de marcenaria pelo mundo — Serras & Formas",
  "Mestres, canais de YouTube, revistas, escolas e bancos de dados de marcenaria do Brasil, EUA, Inglaterra, Japão, França e outros países.", refs, "referencias"))

# ---- galeria ----
gal = '<div class="wrap"><div class="cabeca"><h1>Galeria</h1><p>A oficina, as ferramentas e algumas peças. Toque numa foto para abrir o artigo relacionado.</p></div><div class="fotos">'
gal += "".join(f'<a class="foto" href="{(f["link"].replace("artigo-", "artigo-", 1) + ".html") if f.get("link") else "galeria.html"}"><img src="{e(f["src"])}" alt="{e(f["alt"])}" loading="lazy"><span>{e(f.get("legenda",""))}</span></a>' for f in F)
gal += "</div></div>"
w("galeria.html", pagina("galeria.html", "Galeria — Serras & Formas", "Fotos da oficina, das máquinas e das peças do Serras & Formas.", gal, "galeria"))

# ---- 404, robots e sitemap ----
w("404.html", pagina("404.html", "Página não encontrada — Serras & Formas", "Página não encontrada.",
  '<div class="wrap"><div class="cabeca"><h1>Página não encontrada</h1><p>O endereço pode ter mudado. <a href="biblioteca.html" style="color:var(--mata)">Voltar à biblioteca</a>.</p></div></div>'))
paginas = ["", "biblioteca.html", "referencias.html", "galeria.html"] + [pag_secao(s[0]) for s in SECOES] + [pag_artigo(a) for a in A]
base = DOM.rstrip("/") + "/"
w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
  "".join(f"  <url><loc>{base}{p}</loc></url>\n" for p in paginas) + "</urlset>\n")
w("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {base}sitemap.xml\n")

print("ok", len(os.listdir(OUT)), "arquivos na raiz")
