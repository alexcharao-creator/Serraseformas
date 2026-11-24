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
 ("formacao","Formação","Escolas e cursos presenciais, no Brasil e no exterior: onde ir para ter aula."),
 ("historia","História","A origem das ferramentas, dos fabricantes e dos ofícios."),
 ("glossario","Glossário","Vocabulário da marcenaria em português e inglês."),
 ("mestres","Mestres e leituras","Perfis de marceneiros, autores e canais, e resenhas de livros."),
]
SEC = {s[0]: s for s in SECOES}
BANCADA = ["afiacao","ferramentas","maquinas","encaixes","madeiras","acabamento","oficina","projetos"]
MESES = "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()
e = lambda s: html.escape(str(s), quote=True)
sem_tags = lambda h: re.sub(r"<[^>]+>", " ", h)
def minutos(a): return max(1, round(len(sem_tags(a["corpo"]).split()) / 200))
def data_br(s): y, m, dd = map(int, s.split("-")); return f"{dd} de {MESES[m-1]} de {y}"
def plural(n, s, p): return f"{n} {s if n == 1 else p}"
def conta(sid): return sum(1 for a in A if a["secao"] == sid) + (1 if sid == "formacao" else 0)
def pag_artigo(a): return f"artigo-{a['slug']}.html"
def pag_secao(sid): return f"secao-{sid}.html"
def norm(s): return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()

# ---- estilo, símbolos e script das tabelas ----
css = open(os.path.join(FONTE, "estilo.css"), encoding="utf-8").read()
css += "\n.lista a{color:inherit}.sr{position:absolute;left:-9999px}\n.grade .grupo{grid-column:1/-1;margin:0;padding:14px 22px 10px;background:var(--bg);font:600 12px/1.2 system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--mata)}\n.ref-cat{margin:44px 0 6px;scroll-margin-top:90px}.ref-cat>h2{font-size:30px}.ref-cat>p{color:var(--muted);margin:4px 0 18px}.ref-grupo h3{font-size:19px;margin:22px 0 10px;font-weight:400}\n.corpo figure.foto img{max-height:560px;background:#fff;object-fit:contain}.corpo figure.foto figcaption strong{color:var(--ink,#1d2a22)}.corpo .credito{display:block;font-size:12px;margin-top:4px;opacity:.85}.corpo .credito a{color:inherit}.corpo .par.fotos2{align-items:start}.corpo .par.fotos2 img{aspect-ratio:auto;max-height:420px;object-fit:contain}.corpo .ver-museu{border:1px dashed var(--line);border-radius:10px;padding:14px 18px;margin:20px 0;background:var(--card)}.corpo .ver-museu p{margin:4px 0;font-size:15px}.corpo .ver-museu .vm-t{font-weight:600}@media(max-width:600px){.corpo .par.fotos2{grid-template-columns:1fr}}\n"
simbolos = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="lupa" viewBox="0 0 20 20"><circle cx="8.5" cy="8.5" r="6" fill="none" stroke="currentColor" stroke-width="2"/><path d="M13 13l5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></symbol></svg>'
stack_js = """<script>new MutationObserver(()=>{for(const c of document.querySelectorAll('.stack td:not([data-l])')){let i=0,p=c;while(p=p.previousElementSibling)i+=p.colSpan;c.dataset.l=c.closest('table').rows[0].cells[i]?.textContent||''}}).observe(document,{childList:true,subtree:true})</script>"""
ESCOLAS, PAUTAS = ler("escolas"), ler("pautas")
ASSINATURA = open(os.path.join(FONTE, "assinatura.svg"), encoding="utf-8").read()

def pagina(nome, titulo, descricao, corpo, ativo=""):
    def item(href, rot, k):
        cur = ' aria-current="page"' if k == ativo else ""
        return f'<a href="{href}"{cur}>{rot}</a>'
    nav = item("index.html","Início","inicio") + item("biblioteca.html","Biblioteca","biblioteca") + item("escolas.html","Escolas e cursos","cursos") + item("referencias.html","Referências","referencias") + item("galeria.html","Galeria","galeria")
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
{'<script src="fotos.js"></script>' if re.search(r'<img[^>]+src="https?://', corpo) else ""}
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

def miniatura(a):
    u = foto_de(a)
    return u.replace("/960px-", "/330px-") if "thumb.wikimedia.org" in u else u
def item_lista(a, foto=False):
    s = SEC[a["secao"]][1]
    mini = f'<img class="mini" src="{miniatura(a)}" alt="" loading="lazy">' if foto else ""
    return f'<li data-s="{a["secao"]}"><a href="{pag_artigo(a)}">{mini}<h3>{e(a["titulo"])}</h3><p>{e(a["resumo"])}</p><span class="meta"><b>{e(s)}</b>{e(a["tipo"])} · {minutos(a)} min</span></a></li>'

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
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fotos.js"), os.path.join(OUT, "fotos.js"))

# ---- início ----
oficina = next((a for a in A if a["slug"] == "como-montar-sua-oficina"), A[0])
def cartao(sid, nome, desc): return f'<a href="{pag_secao(sid)}"><h3>{nome}<span>{conta(sid) or "em breve"}</span></h3><p>{desc}</p></a>'
grade = '<p class="grupo">Na bancada</p>' + "".join(cartao(*x) for x in SECOES if x[0] in BANCADA)
grade += '<p class="grupo">Para ler e aprender</p>' + "".join(cartao(*x) for x in SECOES if x[0] not in BANCADA)
grade += f'<a href="referencias.html"><h3>Referências<span>{sum(len(p["itens"]) for p in R)}</span></h3><p>Canais do YouTube, sites e cursos online, livros, revistas e lojas do mundo todo.</p></a>'
cursos = "".join(f'<a href="{e(x["u"]) if x["u"] else "#cursos"}"{" target=\"_blank\" rel=\"noopener\"" if x["u"] else ""}><span class="tipo">{e(x["local"])}</span><strong>{e(x["nome"])}</strong><p>{e(x["d"])}</p><em>{e(x.get("em") or ("Site e cursos" if x["u"] else "Agenda a confirmar"))}</em></a>' for x in ESCOLAS)
pautas = "".join(f'<li><small>{e(x["s"])} · {e(x["st"])}</small><b>{e(x["t"])}</b><span>{e(x["d"])}</span></li>' for x in PAUTAS)
bloco_pautas = (f'<section class="band faixa-clara"><div class="wrap"><span class="eyebrow">Próximos artigos</span><h2>Em preparação</h2><p class="contagem" style="margin-bottom:18px">Pautas planejadas, ainda não publicadas.</p><ul class="pautas">{pautas}</ul></div></section>') if PAUTAS else ""
def foto_de(a):
    if a["slug"] == "como-montar-sua-oficina": return "media/oficina-desengrosso-entrada.webp"
    imgs = re.findall(r'<img src="([^"]+)"', a["corpo"])
    return next((u for u in imgs if not u.lower().endswith(".png")), imgs[0] if imgs else "media/pedra-itaipava.webp")
GUIAS = ["como-montar-sua-oficina", "plainas-de-metal-guia", "regulagem-serra-de-fita", "graminho-tipos-uso-e-exercicios", "cinco-exercicios-plaina", "afiacao-metodo-morito", "espiga-e-furo", "escolher-armazenar-madeira"]
POR = {a["slug"]: a for a in A}
def slide(a, n):
    if a["slug"] == "como-montar-sua-oficina":
        olho, tit = "Organização do espaço · 17,3 m²", "Quer montar sua oficina e não sabe por onde começar?"
        txt = "Uma garagem de 6,40 × 2,70 m serve de estudo de caso para discutir layout, circulação, posição das máquinas, bancada, iluminação, energia, armazenamento e controle de pó. Não é um modelo a copiar: é um ponto de partida para pensar no seu espaço."
    else:
        olho, tit, txt = f'{SEC[a["secao"]][1]} · {minutos(a)} min de leitura', e(a["titulo"]), e(a["resumo"])
    return f'<a class="feature" href="{pag_artigo(a)}"><img src="{foto_de(a)}" alt="" loading="{"eager" if n == 0 else "lazy"}"><div><span class="eyebrow">{olho}</span><h3>{tit}</h3><p>{txt}</p><span class="mais">Ler o guia completo →</span></div></a>'
guias = [POR[g] for g in GUIAS if g in POR]
BLOCO_GUIAS = f'''<section class="band guias-band cor-verde"><div class="wrap">
<span class="eyebrow">Primeiro guia publicado</span><h2>Comece pela oficina</h2>
<div class="arraste"><span>Arraste para o lado para ver outros guias</span><span class="setas"><button type="button" data-d="-1" aria-label="Guia anterior">←</button><button type="button" data-d="1" aria-label="Próximo guia">→</button></span></div>
<div class="carrossel" tabindex="0" aria-label="Guias publicados">{"".join(slide(a, n) for n, a in enumerate(guias))}</div>
</div></section>
<script>(()=>{{const c=document.querySelector('.carrossel');document.querySelectorAll('.arraste button').forEach(b=>b.onclick=()=>c.scrollBy({{left:b.dataset.d*c.clientWidth*.9,behavior:'smooth'}}))}})()</script>'''
BLOCO_RECENTES = f'''<section class="band recentes cor-ouro"><div class="wrap"><div class="titulo-bloco"><div><span class="eyebrow">Novidades</span><h2>Publicados recentemente</h2></div></div>
<ul class="lista com-foto">{"".join(item_lista(a, True) for a in A[:4])}</ul>
<p class="ver-mais"><a href="biblioteca.html">Veja mais publicações →</a></p></div></section>'''
inicio = f"""<section class="hero"><div class="wrap hero-grid">
<div><span class="eyebrow">Petrópolis · Serra Fluminense</span>
<h1>O prazer de aprender, criar e compartilhar.</h1>
<p class="sub">Guias, ferramentas, projetos e técnicas de marcenaria em português. Um acervo pessoal de descobertas, estudos e experiências.</p>
<div class="botoes"><a class="btn" href="biblioteca.html">Explorar o acervo</a><a class="btn sec" href="#sobre">Conheça o projeto</a></div>
<form class="busca" role="search" action="biblioteca.html" method="get"><svg aria-hidden="true"><use href="#lupa"/></svg><label class="sr" for="q-inicio">Buscar no acervo</label><input id="q-inicio" name="q" type="search" placeholder="Buscar: afiação, serra de fita, encaixe…" autocomplete="off"></form>
</div>
<figure><img src="media/pedra-itaipava.webp" alt="Vista das montanhas da região de Itaipava a partir de Nogueira, Petrópolis"><figcaption>A paisagem que inspira o Serras &amp; Formas: Nogueira, Petrópolis.</figcaption></figure>
</div></section>

<section class="band" id="sobre"><div class="wrap intro so">
<div><span class="eyebrow">Por que este site existe</span><h2>Um caderno aberto de marcenaria</h2>
<p>Já procurou como afiar um formão, regular uma plaina ou escolher a lixa certa e só achou resposta em inglês, em vídeos soltos ou em lojas querendo vender? O melhor da marcenaria está em livros e revistas de outros idiomas.</p>
<p>Para devolver à bancada o tempo gasto juntando peças soltas da internet, criei o Serras &amp; Formas: guias práticos, projetos, estudos de ferramentas e traduções comentadas, em português e com as fontes.</p>
<p>Sou um entusiasta com uma pequena oficina na serra de Petrópolis. Não sou profissional, mas anoto o que aprendo para que a sua próxima peça saia melhor.</p>
<div class="assina">{ASSINATURA}<span>Petrópolis, Serra Fluminense</span></div></div>

</div></section>

{BLOCO_RECENTES}

{BLOCO_GUIAS}

<section class="band faixa-clara cor-branca"><div class="wrap">
<div class="titulo-bloco"><div><span class="eyebrow">Biblioteca em construção</span><h2>Explore por assunto</h2></div><a href="biblioteca.html">Ver o acervo inteiro</a></div>
<div class="grade">{grade}</div></div></section>

{bloco_pautas}

<section class="band" id="cursos"><div class="wrap">
<div class="titulo-bloco"><div><span class="eyebrow">Formação presencial</span><h2>Escolas e cursos</h2></div><a href="secao-formacao.html">Escolas no exterior</a></div>
<p class="lede" style="max-width:62ch;color:var(--muted);margin:0 0 22px">Minha recomendação mais importante para quem está começando: <strong>procure aulas práticas com orientação de profissionais</strong>. Nada substitui um professor ao lado da bancada. Reuni {len(ESCOLAS)} escolas e mestres no Brasil, separados por estado, com uma resenha de cada um.</p>
<p class="ver-escolas"><a class="botao-escolas" href="escolas.html">Clique aqui para conhecer as escolas →</a></p>
<p class="lede" style="margin:24px 0 0;color:var(--muted)">No exterior: escolas nos <a href="artigo-escolas-de-marcenaria-eua.html">Estados Unidos</a>, no <a href="artigo-escolas-de-marcenaria-canada.html">Canadá</a>, na <a href="artigo-escolas-de-marcenaria-reino-unido.html">Inglaterra e Escócia</a>, na <a href="artigo-escolas-de-marcenaria-franca.html">França</a>, na <a href="artigo-escolas-de-marcenaria-espanha.html">Espanha</a> e <a href="artigo-escolas-de-marcenaria-pelo-mundo.html">pelo mundo</a>. Prefere aprender online? <a href="referencias.html">Canais, sites e livros →</a></p><p class="discreto"><a href="fabricantes.html">Quem faz as ferramentas? Conheça os fabricantes →</a></p></div></section>

<section class="band seguranca" id="seguranca"><div class="wrap">
<span class="eyebrow">Antes de começar</span><h2>Segurança em primeiro lugar</h2>
<p>Ferramentas cortantes, máquinas de alta rotação e poeira podem causar acidentes graves.</p>
<p>Este site reúne estudos e experiência pessoal: não substitui cursos presenciais, manuais dos fabricantes nem a orientação de profissionais. Cada leitor responde pelos riscos que assume.</p>
<p>Antes de operar máquinas, faça um curso, conheça os procedimentos de cada equipamento e use proteção adequada. Trabalhar com segurança faz parte da arte.</p>
</div></section>"""
w("index.html", pagina("index.html", "Serras & Formas — Artigos e técnicas de marcenaria",
  "Guias, técnicas, projetos, glossário e estudos de marcenaria em português, reunidos por um entusiasta de marcenaria em Petrópolis, Serra Fluminense.", inicio, "inicio"))

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
    extra = ""
    if sid == "formacao":
        extra = f'<li data-s="formacao"><a href="escolas.html"><h3>Escolas de marcenaria no Brasil</h3><p>Mestres e escolas brasileiras com cursos presenciais: {len(ESCOLAS)} endereços, de Cruzeiro (SP) a Nova Friburgo (RJ) e Campo Alegre (SC). Lista completa, separada por estado.</p><span class="meta"><b>Formação</b>Lista por estado</span></a></li>'
    corpo += (f'<p class="contagem">{plural(len(lista) + (1 if extra else 0),"item","itens") if extra else plural(len(lista),"artigo","artigos")}</p><ul class="lista">{extra}{"".join(item_lista(a) for a in lista)}</ul>' if lista
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
CATS = [("canais","Canais do YouTube","Para assistir: quem ensina em vídeo.",("Canal",)),
        ("sites","Sites e cursos online","Para ler e estudar no seu ritmo: blogs, cursos online, bancos de dados e encontros.",("Site","Banco de dados","Evento")),
        ("livros","Livros e editoras","Para ter na estante.",("Livro","Editora")),
        ("revistas","Revistas","Técnica, projetos e testes, com décadas de acervo.",("Revista",)),
        ("lojas","Fabricantes, lojas e fóruns","Quem faz ferramentas de qualidade, onde comprar e comunidades para tirar dúvidas.",("Fabricante","Loja","Fórum"))]
def link_ref2(it):
    u = link_ref(it); ext = u.startswith("http")
    return u, (' target="_blank" rel="noopener"' if ext else "")
def onde2(it):
    u = it.get("u") or ""
    return "Neste site" if u and not u.startswith("http") else onde(it)
total = sum(len(p["itens"]) for p in R)
refs = f'<div class="wrap"><div class="cabeca"><h1>Referências</h1><p>{total} canais, sites, cursos online, livros, revistas e lojas de {len(R)} países, comentados em português. Aqui está o que se aprende pela tela ou pelo papel. Para ter aula presencial, veja <a href="escolas.html">Escolas e cursos</a>. Uma seleção maior de sites, por língua, está em <a href="artigo-sites-de-marcenaria-pelo-mundo.html">Sites de marcenaria pelo mundo</a>.</p></div>'
refs += '<div class="paises claro" style="margin-bottom:12px">' + "".join(f'<a href="#{cid}">{cn}</a>' for cid, cn, _, tps in CATS if any(it["tipo"] in tps for p in R for it in p["itens"])) + "</div>"
for cid, cn, cd, tps in CATS:
    grupos = [(p, [it for it in p["itens"] if it["tipo"] in tps]) for p in R]
    grupos = [(p, its) for p, its in grupos if its]
    if not grupos: continue
    n = sum(len(its) for _, its in grupos)
    refs += f'<section class="ref-cat" id="{cid}"><h2>{cn}</h2><p>{cd} {plural(n,"referência","referências")}.</p>'
    for p, its in grupos:
        refs += f'<div class="ref-grupo"><h3>{p["pais"]}</h3><div class="refs">'
        for it in its:
            u, tg = link_ref2(it)
            refs += f'<a href="{e(u)}"{tg}><span class="tipo">{e(it["tipo"])}</span><strong>{e(it["n"])}</strong><p>{e(it["d"])}</p><em>{e(onde2(it))}</em></a>'
        refs += "</div></div>"
    refs += "</section>"
refs += "</div>"
w("referencias.html", pagina("referencias.html", "Referências de marcenaria: canais, sites, livros e revistas — Serras & Formas",
  "Canais de YouTube, sites e cursos online, livros, editoras, revistas e lojas de marcenaria do Brasil, EUA, Inglaterra, Japão, França e outros países.", refs, "referencias"))

# ---- escolas ----
UFS = {"SP": "São Paulo", "RJ": "Rio de Janeiro", "SC": "Santa Catarina", "RS": "Rio Grande do Sul", "MG": "Minas Gerais", "PR": "Paraná"}
por_uf = {}
for x in ESCOLAS:
    uf = x["local"].rsplit(",", 1)[-1].strip()
    por_uf.setdefault(uf, []).append(x)
ordem = sorted(por_uf, key=lambda u: (-len(por_uf[u]), UFS.get(u, u)))
esc = f'<div class="wrap"><div class="cabeca"><h1>Escolas e cursos de marcenaria no Brasil</h1><p>Minha recomendação mais importante para quem está começando é ter aulas práticas com orientação de profissionais. Aqui estão {len(ESCOLAS)} escolas e mestres, separados por estado. Confirme diretamente com cada um as turmas, os requisitos e a disponibilidade.</p></div>'
esc += '<div class="paises claro" style="margin-bottom:12px">' + "".join(f'<a href="#{u.lower()}">{UFS.get(u, u)}</a>' for u in ordem) + "</div>"
for u in ordem:
    esc += f'<section class="ref-cat" id="{u.lower()}"><h2>{UFS.get(u, u)}</h2><div class="refs">'
    for x in por_uf[u]:
        href = e(x["u"]) if x["u"] else "#"
        alvo = ' target="_blank" rel="noopener"' if x["u"] else ""
        esc += f'<a href="{href}"{alvo}><span class="tipo">{e(x["local"])}</span><strong>{e(x["nome"])}</strong><p>{e(x["d"])}</p><em>{e(x.get("em") or ("Site e cursos" if x["u"] else "Agenda a confirmar"))}</em></a>'
    esc += "</div></section>"
esc += '<p class="lede" style="margin:28px 0 0;color:var(--muted)">No exterior: escolas nos <a href="artigo-escolas-de-marcenaria-eua.html">Estados Unidos</a>, no <a href="artigo-escolas-de-marcenaria-canada.html">Canadá</a>, na <a href="artigo-escolas-de-marcenaria-reino-unido.html">Inglaterra e Escócia</a>, na <a href="artigo-escolas-de-marcenaria-franca.html">França</a>, na <a href="artigo-escolas-de-marcenaria-espanha.html">Espanha</a> e <a href="artigo-escolas-de-marcenaria-pelo-mundo.html">pelo mundo</a>.</p></div>'
w("escolas.html", pagina("escolas.html", "Escolas e cursos de marcenaria no Brasil — Serras & Formas",
  "Escolas e mestres de marcenaria com cursos presenciais no Brasil, separados por estado: São Paulo, Rio de Janeiro, Rio Grande do Sul e Santa Catarina.", esc, "cursos"))

# ---- fabricantes ----
FAB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fabricantes.json"), encoding="utf-8"))
nf = sum(len(p["itens"]) for p in FAB)
fab = f'<div class="wrap"><div class="cabeca"><h1>Fabricantes</h1><p>Quem faz as ferramentas: {nf} fabricantes de {len(FAB)} países, do artesão que faz uma plaina por vez às oficinas que abastecem o mundo. A lista vai crescer; para escolas, veja <a href="escolas.html">Escolas e cursos</a>, e para lojas, canais e livros, as <a href="referencias.html">Referências</a>.</p></div>'
fab += '<div class="paises claro" style="margin-bottom:12px">' + "".join(f'<a href="#{p["id"]}">{p["pais"]}</a>' for p in FAB) + "</div>"
for p in FAB:
    fab += f'<section class="ref-cat" id="{p["id"]}"><h2>{p["pais"]}</h2><div class="refs">'
    for it in p["itens"]:
        fab += f'<a href="{e(it["u"])}" target="_blank" rel="noopener"><span class="tipo">{e(it["local"])}</span><strong>{e(it["n"])}</strong><p>{e(it["d"])}</p><em>{e(it["faz"])}</em></a>'
    fab += "</div></section>"
fab += "</div>"
w("fabricantes.html", pagina("fabricantes.html", "Fabricantes de ferramentas de marcenaria — Serras & Formas",
  "Fabricantes de ferramentas manuais de marcenaria no Brasil, Estados Unidos, Canadá, Inglaterra e Alemanha: plainas, formões, serrotes e morsas.", fab, "referencias"))

# ---- galeria ----
gal = '<div class="wrap"><div class="cabeca"><h1>Galeria</h1><p>A oficina, as ferramentas e algumas peças. Toque numa foto para abrir o artigo relacionado.</p></div><div class="fotos">'
gal += "".join(f'<a class="foto" href="{(f["link"].replace("artigo-", "artigo-", 1) + ".html") if f.get("link") else "galeria.html"}"><img src="{e(f["src"])}" alt="{e(f["alt"])}" loading="lazy"><span>{e(f.get("legenda",""))}</span></a>' for f in F)
gal += "</div></div>"
w("galeria.html", pagina("galeria.html", "Galeria — Serras & Formas", "Fotos da oficina, das máquinas e das peças do Serras & Formas.", gal, "galeria"))

# ---- 404, robots e sitemap ----
w("404.html", pagina("404.html", "Página não encontrada — Serras & Formas", "Página não encontrada.",
  '<div class="wrap"><div class="cabeca"><h1>Página não encontrada</h1><p>O endereço pode ter mudado. <a href="biblioteca.html" style="color:var(--mata)">Voltar à biblioteca</a>.</p></div></div>'))
paginas = ["", "biblioteca.html", "referencias.html", "escolas.html", "fabricantes.html", "galeria.html"] + [pag_secao(s[0]) for s in SECOES] + [pag_artigo(a) for a in A]
base = DOM.rstrip("/") + "/"
w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
  "".join(f"  <url><loc>{base}{p}</loc></url>\n" for p in paginas) + "</urlset>\n")
w("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {base}sitemap.xml\n")

print("ok", len(os.listdir(OUT)), "arquivos na raiz")
