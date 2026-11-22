# Serras & Formas

Biblioteca de marcenaria em língua portuguesa. Site estático (HTML, CSS e um pouco de JavaScript), publicado na Hostinger a partir deste repositório: cada mudança no ramo `main` vai ao ar automaticamente.

## Como publicar um artigo novo

1. Acrescente o artigo no início da lista em `_fonte/artigos.json` (campos: `slug`, `titulo`, `secao`, `tipo`, `data` AAAA-MM-DD, `resumo`, `corpo` em HTML, `fontes`).
2. Fotos e vídeos novos vão em `media/` (fotos com até 1600 px, vídeos em MP4 720p). Para a galeria, acrescente uma entrada em `_fonte/fotos.json`.
3. Na raiz do repositório, rode `python3 _fonte/gerar.py`.
4. Faça commit e push no `main`.

Seções válidas: afiacao, ferramentas, maquinas, encaixes, madeiras, acabamento, oficina, projetos, traducoes, formacao, historia, glossario, cronicas.

Outros arquivos em `_fonte/`:
- `estilo.css`: o visual do site (verde-floresta, dourado, creme, títulos serifados).
- `escolas.json`: a lista "Onde aprender" da página inicial.
- `pautas.json`: os próximos artigos ("Em preparação"). Quando um deles for publicado, retire-o daqui.
- `gerar.py`: monta todas as páginas.
Referências por país ficam em `_fonte/referencias.json`.
A pasta `_fonte/` não é servida ao público (`.htaccess`).
