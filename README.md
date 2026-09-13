# Gerador Automático de Carrosséis de Signos para TikTok

Automação em Python que, a cada execução, pesquisa um assunto em alta,
transforma esse assunto em um tema de signos, gera o carrossel de 6 imagens
(capa + 5 signos), a legenda e as hashtags — e salva tudo pronto pra você
revisar e publicar manualmente no TikTok.

**Esta versão NÃO publica nada automaticamente.** Ela só monta o pacote na
pasta `output/`.

---

## 1. Instalação

```bash
cd tiktok_signos
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Abra o `.env` e preencha o que for usar (veja a seção 5 — nada é obrigatório
para rodar).

## 2. Uso do dia a dia

```bash
python main.py
```

Isso faz o fluxo completo: pesquisa tendências → escolhe o assunto →
gera o conteúdo → valida o português → gera as 6 imagens → salva
`post.json` e `legenda.txt` numa pasta `output/AAAA-MM-DD_titulo/`.

Depois é só:

```text
abrir output/
↓
pegar a pasta do dia
↓
revisar rapidamente
↓
publicar manualmente no TikTok
```

### Modo de teste (sem internet, sem IA)

```bash
python main.py --test
```

Usa um tema fictício e o banco de conteúdo local, só para validar layout
e pipeline. Já vem um exemplo gerado em `output/` para você abrir direto.

### Forçar um tema específico

```bash
python main.py --topic "Top 5 signos que mais fazem drama"
```

Pula a pesquisa de tendências e usa exatamente o tema informado.

Para ajustar o tom da IA em uma execução:

```bash
python main.py --instruction "Seja mais incisivo e provocador, sem fazer acusações não confirmadas."
```

Também é possível deixar uma instrução padrão em `EXTRA_AI_INSTRUCTION` no
arquivo `.env`. A IA recebe como referência uma média de `315` a `318`
caracteres no texto e `114` a `118` caracteres na frase, mas a resposta da IA
é preservada integralmente, sem corte, preenchimento ou bloqueio por tamanho.
 A `phrase` deve ser uma fala curta, entre aspas, escrita como se fosse o
 próprio signo comentando o tema e o texto principal. As aspas são garantidas
 visualmente na imagem mesmo se a API esquecer de incluí-las no JSON.

### Onde ajustar cada coisa

| O que você quer alterar | Arquivo e local |
|---|---|
| Tom, humor e regras gerais da IA | `src/content_generator.py`, variável `_SYSTEM_PROMPT` |
| Estrutura do JSON e instruções do tema | `src/content_generator.py`, variável `_USER_PROMPT_TEMPLATE` |
| Tom de uma execução | `--instruction` no comando |
| Tom padrão de todas as execuções | `EXTRA_AI_INSTRUCTION` no `.env` |
| Limites mínimo/máximo aceitos | `config/config.py`, `MIN_*` e `MAX_*` |
| Alvo médio recomendado | `config/config.py`, `TARGET_*` |
| Consultas de tendências | `config/config.py`, `GOOGLE_NEWS_RSS_QUERIES` |
| Cores, fontes e identidade | `config/config.py` |
| Posições e tamanhos das imagens | `src/image_generator.py` |

Não coloque uma instrução de “cortar” ou “completar com a mesma frase” no
prompt. O projeto envia a orientação de média para a IA e preserva a resposta
completa que ela retornar.

---

## 3. O que o sistema faz em cada execução

```text
Pesquisar tendências (Google News RSS)
    ↓ (se falhar)
NewsAPI, se houver chave configurada
    ↓ (se falhar)
Banco de temas interno (sempre disponível, offline)
    ↓
Pontuar cada assunto por potencial de engajamento
    ↓
Selecionar o melhor assunto (evitando repetir os últimos usados)
    ↓
Transformar o assunto em tema de signos usando a IA configurada
    ↓
Validar português (ortografia básica, tamanho, PT-PT, truncamento)
    ↓
Gerar 6 imagens com o template fixo (templates/capa.png e templates/signo.png)
    ↓
Gerar legenda + hashtags dinâmicas
    ↓
Salvar tudo em output/AAAA-MM-DD_titulo/
```

O modo `--test` usa o banco local. Na produção, se a IA falhar, o sistema
interrompe sem criar um post com tema chumbado no lugar da tendência real.

---

## 4. Identidade visual (layout fixo)

O briefing original pede que a IA **não invente um layout novo a cada
execução** — só o conteúdo muda. Por isso:

 `templates/capa.png` e `templates/signo.png` são as referências fixas de
  tamanho e composição. O conteúdo demonstrativo desses PNGs não é copiado
  para o output.
 As fontes usadas ficam em `fonts/computer-says-no.otf`,
  `fonts/Kapsalon Brush DEMO.otf`, `fonts/Cardo-Regular.ttf` e
  `fonts/label.ttf`, conforme o papel visual de cada elemento.
  quando as tiver — os textos que vi nas suas imagens de referência (título
  numa fonte bold arredondada, corpo numa serifada, selo numa mono) usam
  fontes livres parecidas (Poppins Bold / Lora / DejaVu Sans Mono) só como
  placeholder, já que não tenho os arquivos originais da fonte do canal.
- Cores, margens e posições dos elementos ficam centralizadas em
  `config/config.py` (`COLOR_BACKGROUND`, `COLOR_ACCENT` etc.).

---

## 5. Variáveis de ambiente (`.env`)

| Variável | Obrigatória? | Efeito se vazia |
|---|---|---|
| `AI_PROVIDER` | Sim para produção | `gemini` ou `openai` |
| `GEMINI_API_KEY` | Sim se provider for Gemini | Chave da API Gemini |
| `GEMINI_MODEL` | Não | Usa o modelo definido no `.env.example` |
| `OPENAI_API_KEY` | Sim se provider for OpenAI | Chave da API OpenAI |
| `OPENAI_MODEL` | Não | Usa `gpt-4o-mini` por padrão |
| `NEWS_API_KEY` | Não | Pula direto para o banco de temas interno |
| `BRAND_HANDLE` / `BRAND_NAME` | Não | Usa `@vambora.astro` / `VAMBORA` como placeholder |
| `EXTRA_AI_INSTRUCTION` | Não | Ajusta o tom/abordagem enviada à IA |

O RSS do Google funciona sem chave. Para produção, configure a chave do
provider escolhido. Sem chave, use `python main.py --test` para validar apenas
o layout e o pipeline.

### Consultas de tendências

As consultas ficam em `config/config.py`, na lista `GOOGLE_NEWS_RSS_QUERIES`.
Cada linha é uma busca independente no Google News RSS. Você pode comentar
uma linha com `#`, trocar uma consulta ou adicionar outra:

```python
GOOGLE_NEWS_RSS_QUERIES = [
    "famosos briga",             # notícias de conflitos públicos
    "celebridade traição",       # relacionamentos e rumores noticiados
    # "BBB treta",               # desativada temporariamente
    "reality show polêmica",     # realities e repercussão
]
```

Evite consultas genéricas demais. Prefira termos que tragam notícias atuais,
como `término namoro famoso`, `influencer polêmica` ou `reality show treta`.

### Prompt editável

O prompt é dividido em duas partes em `src/content_generator.py`:

- `_SYSTEM_PROMPT`: personalidade, segurança, idioma e regras de escrita.
- `_USER_PROMPT_TEMPLATE`: tema pesquisado, formato JSON, campos da capa,
  textos dos signos, limites de caracteres e instrução adicional.

Altere o `_SYSTEM_PROMPT` para mudar o comportamento geral. Altere o
`_USER_PROMPT_TEMPLATE` para mudar o que deve ser retornado pela API. Preserve
os campos `carousel_title`, `cover_title`, `subtitle`, `sign`, `text` e
`phrase`, porque o renderizador depende deles.

---

## 6. Estrutura do projeto

```text
tiktok_signos/
├── main.py                  # orquestra o fluxo (enxuto, sem lógica pesada)
├── config/config.py         # todas as configurações centralizadas
├── src/
│   ├── trend_finder.py      # pesquisa de tendências + fallback em cadeia
│   ├── topic_selector.py    # escolhe o melhor assunto e categoriza
│   ├── content_generator.py # gera título/subtítulo/textos (IA ou fallback)
│   ├── fallback_bank.py     # banco de conteúdo local pronto (offline)
│   ├── text_validator.py    # revisão de PT-BR, tamanho, truncamento
│   ├── image_generator.py   # desenha as imagens sobre o template fixo
│   ├── carousel_builder.py  # monta as 6 imagens e a pasta do post
│   ├── caption_generator.py # legenda + hashtags dinâmicas
│   ├── ai_client.py         # única camada que fala com a API de IA
│   └── utils.py             # logging, slugify, histórico, JSON
├── templates/                # capa.png e signo.png (layout fixo)
├── fonts/                     # fontes usadas nas imagens
├── output/                    # pacotes gerados, um por dia/tema
├── logs/run.log                # log de cada execução
└── data/history.json            # histórico p/ evitar repetição de temas
```

---

## 7. Próxima etapa (não incluída nesta versão)

A arquitetura já está pronta para, no futuro, plugar um módulo
`publisher.py` que pegue a pasta gerada em `output/` e publique no TikTok
automaticamente — sem precisar reescrever o pipeline atual. Por enquanto,
por decisão do projeto, essa etapa fica só no papel.
