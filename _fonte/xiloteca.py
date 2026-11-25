"""Xiloteca: fundo de madeira clara em cada página, enxertos de madeiras brasileiras com o nome no centro."""
import hashlib, os, re
from urllib.parse import quote
# ---------- madeiras ----------
# nome: (nome científico, cor base, cor do veio, frequência do veio, faixas escuras?)
CLARAS = {  # nome: (nome científico, cor média de reserva)
 'Pau-marfim':      ('Balfourodendron riedelianum', '#DCC27E'),
 'Freijó':          ('Cordia goeldiana',            '#B9A46E'),
 'Garapa':          ('Apuleia leiocarpa',           '#B8924A'),
 'Caroba':          ('Jacaranda copaia',            '#E2CF96'),
 'Tauari':          ('Couratari guianensis',        '#CDB06A'),
 'Morototó':        ('Schefflera morototoni',       '#BCA77E'),
 'Pinho-do-paraná': ('Araucaria angustifolia',      '#DCC08A'),
 'Pequiá':          ('Caryocar glabrum',            '#D8BE7E'),
 'Cedro':           ('Cedrela fissilis',            '#A9895A'),
 'Pau-mulato':      ('Calycophyllum spruceanum',    '#B8954E'),
 'Cerejeira':       ('Amburana cearensis',          '#9E8A58'),
 'Quaruba':         ('Vochysia guianensis',         '#A88E60'),
 'Sumaúma':         ('Ceiba pentandra',             '#C2B184'),
}
ESCURAS = {
 'Roxinho':      ('Peltogyne spp.',          '#7A3655'),
 'Imbuia':       ('Ocotea porosa',           '#6B5238'),
 'Muiracatiara': ('Astronium lecointei',     '#A0643A'),
 'Angelim-pedra':('Hymenolobium petraeum',   '#9A7A48'),
 'Pau-brasil':   ('Paubrasilia echinata',    '#B0412F'),
 'Ipê':          ('Handroanthus spp.',       '#6A5236'),
 'Itaúba':       ('Mezilaurus itauba',       '#4E4630'),
 'Cumaru':       ('Dipteryx odorata',        '#957044'),
 'Jatobá':       ('Hymenaea courbaril',      '#A2553A'),
 'Sucupira':     ('Bowdichia nitida',        '#6E4E30'),
 'Cabreúva':     ('Myroxylon peruiferum',    '#8E4E32'),
 'Tatajuba':     ('Bagassa guianensis',      '#B98E3E'),
 'Muirapiranga': ('Brosimum rubescens',      '#962F2A'),
 'Pau-amarelo':  ('Euxylophora paraensis',   '#D2AE3C'),
 'Peroba-rosa':  ('Aspidosperma polyneuron', '#C48E6C'),
 'Mogno':        ('Swietenia macrophylla',   '#93452E'),
}

def seed(nome): return int(hashlib.md5(nome.encode()).hexdigest()[:4],16)%900+1

def textura(nome, base, veio, freq, w=900, h=420, forte=1.0):
    s = seed(nome)
    r,g,b = (int(veio[i:i+2],16)/255 for i in (1,3,5))
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}'>"
           f"<filter id='v' x='0' y='0' width='100%' height='100%'>"
           f"<feTurbulence type='fractalNoise' baseFrequency='0.0022 {freq}' numOctaves='4' seed='{s}' stitchTiles='stitch'/>"
           f"<feColorMatrix values='0 0 0 0 {r:.3f} 0 0 0 0 {g:.3f} 0 0 0 0 {b:.3f} {2.4*forte:.2f} 0 0 0 {-1.05*forte:.2f}'/></filter>"
           f"<filter id='p' x='0' y='0' width='100%' height='100%'>"
           f"<feTurbulence type='fractalNoise' baseFrequency='0.02 0.6' numOctaves='2' seed='{s+7}' stitchTiles='stitch'/>"
           f"<feColorMatrix values='0 0 0 0 {r:.3f} 0 0 0 0 {g:.3f} 0 0 0 0 {b:.3f} 1.6 0 0 0 -0.95'/></filter>"
           f"<rect width='100%' height='100%' fill='{base}'/>"
           f"<rect width='100%' height='100%' filter='url(#v)'/>"
           f"<rect width='100%' height='100%' filter='url(#p)' opacity='.55'/></svg>")
    return "url(\"data:image/svg+xml," + quote(svg, safe="=:/'. ") + "\")"

def luminancia(hexc):
    r,g,b = (int(hexc[i:i+2],16) for i in (1,3,5))
    return .299*r+.587*g+.114*b

# ---------- páginas ----------
PAGINAS = {  # pagina: madeira do fundo (enxertos escolhidos automaticamente, misturando tons)
 'index.html':             'Pau-marfim',
 'secao-ferramentas.html': 'Pau-amarelo',
 'secao-afiacao.html':     'Roxinho',
 'secao-encaixes.html':    'Freijó',
 'secao-madeiras.html':    'Pau-brasil',
 'secao-acabamento.html':  'Peroba-rosa',
 'secao-maquinas.html':    'Itaúba',
 'secao-oficina.html':     'Pinho-do-paraná',
 'secao-projetos.html':    'Muirapiranga',
 'secao-historia.html':    'Imbuia',
 'secao-mestres.html':     'Ipê',
 'secao-formacao.html':    'Cerejeira',
 'secao-traducoes.html':   'Mogno',
 'secao-glossario.html':   'Sumaúma',
}
FORMAS = ['retangulo']
# posições (lado, topo em % da página) para até 6 enxertos
POS = [('e',9),('d',20),('e',38),('d',52),('e',70),('d',84)]

import unicodedata as _ud
FOTOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'media', 'madeiras')
def foto(n):
    slug = _ud.normalize('NFKD', n).encode('ascii','ignore').decode().lower()
    return 'media/madeiras/%s.jpg' % slug

_LUM = {}
def lum_foto(n):
    if n not in _LUM:
        try:
            from PIL import Image
            im = Image.open(os.path.join(FOTOS_DIR, os.path.basename(foto(n)))).convert('L').resize((1,1))
            _LUM[n] = im.getpixel((0,0))
        except Exception:
            _LUM[n] = luminancia(ESCURAS[n][1])
    return _LUM[n]

# Fotos reais (amostras de xiloteca): CIRAD via Wikimedia Commons, domínio público;
# Pau-amarelo: "Brya", CC BY-SA 4.0; Pau-brasil: "Fopseh", CC BY-SA 4.0.
CREDITO = ('Amostras de madeira: fotografias reais da Xiloteca do CIRAD (domínio público, via Wikimedia Commons); '
           'Pau-amarelo, foto de Brya, e Pau-brasil, foto de Fopseh, ambas CC BY-SA 4.0.')

def fundo_foto(n):
    return foto(n).replace('media/madeiras/','media/madeiras/fundo-')

def enxertos(lista, css):
    out=[]
    for i,n in enumerate(lista):
        sci, base = sci_de(n), base_de(n)
        forma = FORMAS[0]
        lado, top = POS[i % len(POS)]
        claro = lum_foto(n) > 150
        css.append(f'.enx[data-m="{i}"]{{background:{base} url({foto(n)}) center/cover no-repeat}}')
        out.append(f'<figure class="enx {forma} {lado}{" claro" if claro else ""}" style="top:{top}%" data-m="{i}" title="{n} ({sci}), amostra real">'
                   f'<span class="nm">{n}</span><em>{sci}</em></figure>')
    return '<div class="xiloteca" aria-label="Xiloteca: amostras reais de madeiras brasileiras">' + ''.join(out) + '</div>'

CSS = r"""
/* ===== Prévia xiloteca ===== */
body.madeira{color-scheme:light;background-size:1400px 680px;position:relative}
body.madeira main{position:relative;z-index:1}
body.madeira .band,body.madeira .cor-ouro,body.madeira .cor-verde,body.madeira .cor-branca,body.madeira .faixa-clara,body.madeira .seguranca{background:transparent!important;color:#2b2b26}
body.madeira .band{padding:clamp(18px,3vw,36px) 0}
/* folha branca com moldura dupla, como no livro */
body.madeira .band>.wrap,body.madeira:not(.pg-artigo) main>.wrap{background:#fff;max-width:980px;margin:0 auto;padding:clamp(28px,4.5vw,56px) clamp(22px,5vw,64px);
  border:1px solid #c7a560;outline:1px solid #c7a560;outline-offset:-8px;box-shadow:0 8px 28px rgba(60,45,15,.10);position:relative;z-index:1}
body.madeira:not(.pg-artigo) main>.wrap{margin-top:40px;margin-bottom:48px}
body.madeira .hero{position:relative;z-index:1}
/* títulos minimalistas */
body.madeira .band h2,body.madeira:not(.pg-artigo) .cabeca h1{font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;text-transform:uppercase;letter-spacing:.14em;font-weight:800;color:#1f1f1c;font-size:clamp(22px,2.6vw,30px);line-height:1.25}
body.madeira .band h2::after,body.madeira:not(.pg-artigo) .cabeca h1::after{content:"";display:block;width:64px;height:1px;background:#c7a560;margin:18px 0 6px}
body.madeira .eyebrow,body.madeira .trilha{letter-spacing:.22em;text-transform:uppercase;font-size:12px;color:#8a6a2a!important}
body.madeira .cor-verde *,body.madeira .cor-ouro *{color:inherit}
body.madeira .cor-verde h2,body.madeira .cor-verde h3{color:#1f1f1c}
body.madeira .cor-verde p,body.madeira .cor-ouro p{color:#4a463d}
/* listas de artigos: limpas, numeradas */
body.madeira .lista{counter-reset:n;border-top:1px solid #e3d6b8!important}
body.madeira .lista li{counter-increment:n;background:#fff!important;border:0!important;border-bottom:1px solid #eee3cc!important;box-shadow:none!important;border-radius:0!important;margin:0!important}
body.madeira .lista li a{padding:22px 0!important;background:none!important}
body.madeira .lista h3{font-family:Inter,system-ui,sans-serif;font-weight:700;letter-spacing:.01em;color:#1f1f1c!important}
body.madeira .lista p{color:#55504a!important}
body.madeira .lista .meta b{color:#8a6a2a!important;letter-spacing:.08em;text-transform:uppercase;font-size:11px}
body.madeira .lista:not(.com-foto) li a{position:relative;padding-left:58px!important}
body.madeira .lista:not(.com-foto) li a::before{content:counter(n);position:absolute;left:0;top:22px;font:800 20px/1 Inter,system-ui,sans-serif;color:#c7a560;
  padding-right:12px;border-right:1px solid #c7a560;min-width:28px;text-align:left}
body.madeira .lista.com-foto li a{position:relative}
body.madeira .lista.com-foto .mini{border-radius:0!important;box-shadow:none!important}
body.madeira .lista.com-foto li a::before{content:counter(n);position:absolute;left:8px;top:30px;z-index:2;background:#fff;color:#c7a560;font:800 13px/1 Inter,system-ui,sans-serif;
  width:24px;height:24px;display:grid;place-items:center}
body.madeira .ver-mais a,body.madeira .botao-escolas{background:#1f1f1c!important;color:#fff!important;border-radius:0!important;letter-spacing:.12em;text-transform:uppercase;font-size:13px}
body.madeira .slide,body.madeira .carrossel>*{border-radius:0!important;box-shadow:none!important;border:1px solid #e6dac0!important;background:#fff!important}
body.madeira .slide *{color:#2b2b26}
body.madeira .contagem{letter-spacing:.18em;text-transform:uppercase;font-size:12px;color:#8a6a2a}
body.madeira .seguranca p,body.madeira .seguranca li,body.madeira .seguranca h2,body.madeira #cursos p,body.madeira #sobre p{color:#3b3730!important}
body.madeira .seguranca a,body.madeira #cursos a:not(.botao-escolas){color:#1f1f1c!important}
@media (max-width:760px){body.madeira .band>.wrap,body.madeira:not(.pg-artigo) main>.wrap{margin-left:10px;margin-right:10px;padding:30px 22px;outline-offset:-6px}}
body.madeira .grade .grupo{background:none!important;border-bottom:1px solid #c7a560;color:#8a6a2a!important;letter-spacing:.22em;font-size:11px;padding:0 0 6px!important}
body.madeira .grade a{background:#fff!important;border:1px solid #e6dac0!important;border-radius:0!important;box-shadow:none!important;position:relative;padding-left:38px!important;color:#2b2b26!important}
body.madeira .grade a:hover{border-color:#c7a560!important}
body.madeira .grade a h3{font-family:Inter,system-ui,sans-serif;text-transform:uppercase;letter-spacing:.1em;font-size:13px;font-weight:800;color:#1f1f1c!important}
body.madeira .grade a h3 span{background:none!important;color:#c7a560!important;font-weight:800;border:1px solid #c7a560;border-radius:0!important}
body.madeira .grade a p{color:#55504a!important}
body.madeira .grade a::before{content:"";position:absolute;left:0;top:0;bottom:0;width:20px;background:var(--sw)}
body.madeira .grade a::after{content:attr(data-mad);display:block;margin-top:8px;font:italic 11px/1.2 Georgia,serif;color:#8a6a2a}
body.madeira .carrossel{grid-auto-columns:100%;gap:24px;overflow-x:hidden;scroll-snap-type:x mandatory}
body.madeira .guias-band>.wrap{padding-top:clamp(24px,3vw,40px);padding-bottom:clamp(24px,3vw,40px)}
body.madeira .carrossel{padding-bottom:6px}
body.madeira .carrossel .feature{height:clamp(320px,calc(100vh - 400px),460px);border-radius:0!important;border:1px solid #e6dac0;box-shadow:none}
body.madeira .carrossel .feature img{min-height:0;height:100%}
body.madeira .carrossel .feature>div{overflow:auto;padding:clamp(22px,3vw,40px)}
body.madeira .carrossel .feature h3{font-size:clamp(24px,2.6vw,34px)}
@media(max-width:760px){body.madeira .carrossel{overflow-x:auto}body.madeira .carrossel .feature{height:auto}body.madeira .carrossel .feature img{height:220px}}
/* ===== enxertos ===== */
.xiloteca{position:absolute;inset:0;pointer-events:none;z-index:0}
.enx{position:absolute;width:150px;height:74px;margin:0;background-size:300px 300px;display:flex;flex-direction:column;align-items:center;justify-content:center;
  box-shadow:inset 0 0 0 1px rgba(0,0,0,.35),0 0 0 1px rgba(255,255,255,.35),inset 0 2px 6px rgba(0,0,0,.25);pointer-events:auto;text-align:center}
.enx.e{left:calc(50% - 490px - 182px)}
.enx.d{right:calc(50% - 490px - 182px)}
.enx .nm{font:700 10.5px/1.15 Inter,system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.6);max-width:92%}
.enx em{font:italic 9px/1.2 Georgia,serif;color:rgba(255,255,255,.85);margin-top:3px;text-shadow:0 1px 2px rgba(0,0,0,.6);max-width:88%}
.enx.claro .nm,.enx.claro em{color:#2a2418;text-shadow:0 1px 1px rgba(255,255,255,.5)}
.fundo-legenda{position:relative;z-index:2;width:max-content;max-width:min(92%,600px);margin:8px auto 36px;text-align:center;background:rgba(255,255,255,.92);border:1px solid #c7a560;outline:1px solid #c7a560;outline-offset:-4px;
  padding:8px 14px;font:11px/1.35 Inter,system-ui,sans-serif;letter-spacing:.08em;color:#3b352a}
.fundo-legenda b{text-transform:uppercase;letter-spacing:.14em}
.fundo-legenda em{font-family:Georgia,serif}
.fundo-legenda small{display:block;margin-top:4px;font-size:9.5px;letter-spacing:.02em;color:#6b6252;max-width:560px;white-space:normal}
@media (max-width:1300px){
  .xiloteca{position:relative;inset:auto;display:flex;flex-wrap:wrap;justify-content:center;gap:18px;padding:28px 12px 8px;z-index:1}
  .enx{position:relative;left:auto!important;right:auto!important;top:auto!important;width:132px;height:64px}
}

@media (min-width:1500px){
  .enx{width:210px;height:103px}
  .enx.e{left:calc(50% - 490px - 244px)}
  .enx.d{right:calc(50% - 490px - 244px)}
  body.madeira.pg-artigo .enx.e{left:calc(50% - 410px - 248px)}
  body.madeira.pg-artigo .enx.d{right:calc(50% - 410px - 248px)}
  .enx .nm{font-size:13px}
  .enx em{font-size:11px;margin-top:4px}
}
"""


CSS += r"""
/* artigos: folha branca com moldura dupla sobre a madeira */
body.madeira article.texto{background:#fff;border:1px solid #c7a560;outline:1px solid #c7a560;outline-offset:-8px;border-radius:0;box-shadow:0 8px 28px rgba(60,45,15,.10);position:relative;z-index:1}
body.madeira.pg-artigo .enx.e{left:calc(50% - 410px - 186px)}
body.madeira.pg-artigo .enx.d{right:calc(50% - 410px - 186px)}
body.madeira .cabeca h1{margin-top:4px}
@media (max-width:1180px){body.madeira.pg-artigo .xiloteca{position:relative;inset:auto;display:flex;flex-wrap:wrap;justify-content:center;gap:18px;padding:28px 12px 8px;z-index:1}
 body.madeira.pg-artigo .enx{position:relative;left:auto!important;right:auto!important;top:auto!important;width:132px;height:64px}}
"""

OUTRAS = {'biblioteca.html':'Cabreúva','escolas.html':'Cedro','referencias.html':'Caroba',
          'fabricantes.html':'Jatobá','galeria.html':'Muiracatiara','404.html':'Pau-marfim'}
SEC_ARTIGO = {}   # pagina do artigo -> id da secao (preenchido pelo gerar.py)

def sci_de(n): return (CLARAS.get(n) or ESCURAS[n])[0]
def base_de(n): return (CLARAS.get(n) or ESCURAS[n])[1]

def escolhe(nome, fundo, n=4):
    """Mistura tons: metade claras, metade médias/avermelhadas/escuras, sem repetir o fundo."""
    h = lambda k: hashlib.md5((nome+k).encode()).hexdigest()
    cl = sorted([k for k in CLARAS if k != fundo], key=h)
    es = sorted([k for k in ESCURAS if k != fundo], key=h)
    out = []
    for i in range(n): out.append((es if i % 2 == 0 else cl)[i // 2])
    return out

def plano(nome):
    if nome in PAGINAS:
        f = PAGINAS[nome]; return (f, escolhe(nome, f, 6 if nome == 'index.html' else 4))
    if nome in SEC_ARTIGO:
        f = PAGINAS.get('secao-%s.html' % SEC_ARTIGO[nome], 'Pau-marfim')
        return (f, escolhe(nome, f, 4))
    if nome in OUTRAS: return (OUTRAS[nome], escolhe(nome, OUTRAS[nome], 4))
    return None

def decorar(nome, h):
    p = plano(nome)
    if not p: return h
    fundo, lista = p
    sci, base = sci_de(fundo), base_de(fundo)
    css = [f'body.madeira{{background-color:{base};background-image:url({fundo_foto(fundo)})}}']
    xil = enxertos(lista, css)
    if nome == 'index.html':
        for sp,fd in PAGINAS.items():
            if not sp.startswith('secao-'): continue
            css.append(f'body.madeira .grade a[href="{sp}"]{{--sw:url({fundo_foto(fd)}) center/cover}}')
            h = h.replace(f'<a href="{sp}"><h3>', f'<a href="{sp}" data-mad="Madeira: {fd}"><h3>', 1)
    cls = 'madeira' + (' pg-artigo' if nome in SEC_ARTIGO else '')
    h = h.replace('<link rel="stylesheet" href="style.css">', '<link rel="stylesheet" href="style.css">\n<style>' + '\n'.join(css) + '</style>', 1)
    h = h.replace('<body>', f'<body class="{cls}">', 1)
    leg = (f'<div class="fundo-legenda">Fundo: <b>{fundo}</b> · <em>{sci}</em>'
           f'<small>Fundo e enxertos: fotos reais de amostras, Xiloteca do CIRAD (domínio público, via Wikimedia Commons); '
           f'Pau-amarelo por Brya e Pau-brasil por Fopseh (CC BY-SA 4.0).</small></div>')
    return h.replace('</main>', '</main>\n' + xil + leg, 1)

CSS += r"""
@media (min-width:1500px){
  body.madeira.pg-artigo .enx.e{left:calc(50% - 410px - 248px)}
  body.madeira.pg-artigo .enx.d{right:calc(50% - 410px - 248px)}
}
"""

CSS += r"""
/* rodapé legível sobre qualquer madeira */
body.madeira footer{background:rgba(255,253,247,.95);position:relative;z-index:2;border-top:1px solid #c7a560}
"""
