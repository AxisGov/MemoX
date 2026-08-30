<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/bittencourtthulio/MemoX/main/.github/assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/bittencourtthulio/MemoX/main/.github/assets/banner-light.svg">
  <img alt="memox — a camada de memoria do metodo Expx" src="https://raw.githubusercontent.com/bittencourtthulio/MemoX/main/.github/assets/banner-light.svg" width="100%">
</picture>

<p>
  <img alt="harness: Claude Code" src="https://raw.githubusercontent.com/bittencourtthulio/MemoX/main/.github/assets/badge-claude.svg">
  <img alt="harness: OpenCode" src="https://raw.githubusercontent.com/bittencourtthulio/MemoX/main/.github/assets/badge-opencode.svg">
  <img alt="memoria: indice invertido" src="https://raw.githubusercontent.com/bittencourtthulio/MemoX/main/.github/assets/badge-indice.svg">
  <img alt="embedding: nenhum" src="https://raw.githubusercontent.com/bittencourtthulio/MemoX/main/.github/assets/badge-embedding.svg">
  <img alt="schema expx v1" src="https://raw.githubusercontent.com/bittencourtthulio/MemoX/main/.github/assets/badge-schema.svg">
  <img alt="docs pt-BR" src="https://raw.githubusercontent.com/bittencourtthulio/MemoX/main/.github/assets/badge-lang.svg">
  <img alt="licenca MIT" src="https://raw.githubusercontent.com/bittencourtthulio/MemoX/main/.github/assets/badge-license.svg">
</p>

<strong>A camada de memória do método Expx</strong> — entrega o que o projeto já sabe<br>
sobre um arquivo antes do plano existir, para <a href="https://claude.com/claude-code">Claude Code</a> e <a href="https://opencode.ai">OpenCode</a>.

</div>

`memox` indexa os artefatos que as outras camadas já gravaram — relatórios técnicos, causas raiz, decisões, dívida, lacunas, QA e entregas — e devolve o histórico de um arquivo, de um módulo ou de um termo no momento em que alguém declara que vai tocá-lo.

> **Ele não guarda conhecimento próprio.**
> Toda entrada aponta para um artefato real, com caminho e data. Não existe uma "versão do memox" dos fatos que possa divergir dos artefatos e envelhecer em silêncio — o índice inteiro é descartável e reconstruível do zero.

---

## O ecossistema Expx

O método Expx é um conjunto de skills que se compõem, instaladas e mantidas pelo CLI [`expxdev`](https://github.com/bittencourtthulio/expxdev).

| Peça | Papel | Relação com a `memox` |
|---|---|---|
| **[expxdev](https://github.com/bittencourtthulio/expxdev)** | o CLI: instala, atualiza e diagnostica o ecossistema, e sobe o painel de operação | é quem instala esta skill (`npx expxdev init`) |
| **[sprintx](https://github.com/bittencourtthulio/sprintx)** | **Build** — feature nova, F1…F6 | consulta na F1 e na F3, sobre os arquivos que o plano pretende tocar |
| **[runx](https://github.com/bittencourtthulio/runx)** | **Run** — ocorrência em produção, E1…E5 | consulta na E1 sobre os arquivos impactados; dispara reindexação na E5 |
| **[legadox](https://github.com/bittencourtthulio/legadox)** | **camada** de segurança para código legado | consome regressão e reprovação em QA como entrada do cálculo de raio |
| **[stackx](https://github.com/bittencourtthulio/stackx)** | **camada** de convenções do repositório | fonte independente: as convenções não entram no índice |
| **[mergex](https://github.com/bittencourtthulio/mergex)** | entrega: branch, commit por task, PR e pacote de QA | arquivo com histórico de regressão sobe de faixa de atenção |
| **[prodx](https://github.com/bittencourtthulio/prodx)** | **camada** de produto: decide **se** há trabalho | o índice indexa o `INDICE.md` e os vereditos; é o que faz a verificação de existência melhorar com o tempo |
| **memox** *(este repositório)* | **camada** de memória do projeto | — |

**Camadas** (`memox`, `stackx`, `legadox`, `prodx`) sozinhas não fazem nada — elas modificam o comportamento da `sprintx`, da `runx` e da `mergex`. Sem índice construído, nada muda: as irmãs se comportam como se comportariam sem esta skill.

Detalhes do ecossistema inteiro no [README do expxdev](https://github.com/bittencourtthulio/expxdev).

---

## O problema

Uma software house resolve o mesmo tipo de problema repetidamente. Bug de arredondamento numa faixa de peso hoje; bug parecido no cálculo de comissão em três meses. Quem lembra do primeiro resolve o segundo em vinte minutos. Ninguém lembra.

O conhecimento existe. Está em `01-CAUSA-RAIZ.md`, em `00-DECISOES.md`, em `relatorios/*/tecnico.md`, em `DIVIDA.md`, em `LACUNAS.md` e em `QA.md`. Foi escrito com cuidado, revisado, e está em disco.

O que falta é ele **chegar na hora certa, sem alguém precisar lembrar de procurar**.

Essa é a assimetria que o memox resolve: quem lembra do bug antigo já não precisava da consulta; quem não lembra não sabe que deveria perguntar. Memória que precisa ser consultada não é usada.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/bittencourtthulio/MemoX/main/assets/memox-fluxo-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/bittencourtthulio/MemoX/main/assets/memox-fluxo.svg">
  <img alt="Fluxo do memox: à esquerda, os artefatos gravados por runx, sprintx, mergex e legadox; ao centro, o índice sendo construído a partir deles, com as chaves por arquivo, módulo, decisão e termo e os sinais derivados, entre os quais o de regressão; à direita, a injeção chegando no momento em que um trabalho declara os arquivos que vai tocar, e o sinal de regressão alimentando o cálculo de raio da legadox." src="https://raw.githubusercontent.com/bittencourtthulio/MemoX/main/assets/memox-fluxo.svg" width="100%">
</picture>

## Por que índice, e não RAG

O memox é um **índice invertido**. Não usa embedding, não usa banco vetorial, não resume transcript, não chama modelo para ingerir. A alternativa semântica foi considerada e descartada por três motivos, e eles governam todo o desenho:

1. **A pergunta real não é "o que é semanticamente parecido", é "quem já mexeu neste arquivo e por quê".** Isso é índice invertido, não busca vetorial. A chave de busca é um caminho de arquivo, que é uma string exata.

2. **Resposta de índice é verificável.** Ela aponta arquivo, trabalho e data: dá para abrir o artefato e conferir. Recuperação semântica erra em silêncio — devolve algo plausível, com a mesma confiança com que devolveria o certo.

3. **Índice não custa nada por sessão** e funciona desde o terceiro trabalho fechado. Acervo semântico precisa de volume para valer, e cobra por consulta enquanto não vale.

O memox também **não indexa transcript de conversa**. A fonte são os artefatos, que já foram curados e revisados por humano. Transcript é pensamento em voz alta: contém o caminho descartado com a mesma aparência do caminho adotado — e um índice não tem como distinguir os dois.

---

## Compatibilidade

`memox` funciona em **Claude Code** e em **OpenCode**, a partir da mesma fonte. A skill fica **apenas** em `.claude/skills/` nos dois harnesses — o OpenCode lê `.claude/skills/*/SKILL.md` nativamente, e duplicar a árvore causaria colisão de nome. Só os comandos existem nas duas pastas, porque cada harness lê a sua:

| | Claude Code | OpenCode |
|---|---|---|
| Skill (projeto) | `.claude/skills/memox/` | a mesma pasta, lida nativamente |
| Comandos (projeto) | `.claude/commands/` | `.opencode/commands/` |
| Skill (global) | `~/.claude/skills/memox/` | a mesma pasta |
| Comandos (global) | `~/.claude/commands/` | `~/.config/opencode/command/` |
| Hooks | `.claude/hooks/memox-*.sh` | **lacuna declarada** — ver abaixo |

O `AGENTS.md` na raiz instrui o agente a consultar o índice nos pontos certos, em qualquer harness.

**Hooks são mecanismo do Claude Code.** O OpenCode tem sistema próprio de eventos: enquanto não houver equivalente mapeado, isso é **lacuna declarada, não paridade garantida**. Sem hook, o memox continua funcionando por consulta manual — a perda é que alguém precisa lembrar de perguntar, que é justamente o problema que a injeção resolve.

Requisito: `python3`. O motor usa apenas a biblioteca padrão — sem dependência externa, sem rede.

---

## Instalação

O memox não tem fluxo próprio: ele produz um índice que as outras skills consultam.

### Pelo CLI do método (recomendado)

O [`expxdev`](https://github.com/bittencourtthulio/expxdev) instala o memox por completo — a
skill, os comandos, os dois hooks com bit de execução e o registro em `.claude/settings.json`:

```bash
npx expxdev init --skills sprintx,memox
```

O CLI trata o memox como **camada**: sozinho ele não faz nada, então precisa vir acompanhado de
`sprintx` ou `runx`. Ele avisa se você pedir só a camada, mas nunca impede.

Duas coisas que o CLI garante e que a instalação manual erra com facilidade:

- **o hook e o motor ficam irmãos.** O hook resolve o motor como
  `DIR_HOOK/../skills/memox/assets/memox.py`; se a skill não estiver em `.claude/skills/`, o
  hook sai `0` em silêncio e não faz nada;
- **o registro é idempotente.** Rodar o `init` de novo não duplica a entrada do hook, o que
  faria o memox rodar duas vezes por prompt.

`npx expxdev doctor` acusa `memox-sem-motor` se essa relação quebrar — é o único jeito de ver
uma instalação quebrada, já que o hook falha em silêncio por projeto.

O painel (`npx expxdev panel`) lê o índice e mostra, na seção **Memória**, os arquivos de
risco, as regressões com sua evidência, as coincidências recusadas e os artefatos contaminados.

### Claude Code (manual)

```bash
cp -r .claude/skills/memox      <projeto>/.claude/skills/
cp    .claude/hooks/memox-*.sh  <projeto>/.claude/hooks/
cp    .claude/commands/memox*.md <projeto>/.claude/commands/
cp    AGENTS.md                 <projeto>/
chmod +x <projeto>/.claude/hooks/memox-*.sh
```

Registre os dois hooks em `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/memox-injetar.sh" }] }
    ],
    "Stop": [
      { "hooks": [{ "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/memox-reindexar.sh" }] }
    ]
  }
}
```

### OpenCode

```bash
cp -r .claude/skills/memox         <projeto>/.claude/skills/
cp    .opencode/commands/memox*.md <projeto>/.opencode/commands/
cp    AGENTS.md                    <projeto>/
```

### Verificação

Construa o índice e confira o estado:

```bash
python3 .claude/skills/memox/assets/memox.py indexar
python3 .claude/skills/memox/assets/memox.py estado
```

Ou, dentro do harness, `/memox`. O índice vive em `.expx/memoria/` e **não é versionado**: é derivado e reconstruível a qualquer momento.

---

## Uso

### O jeito mais simples

Não usar. A injeção acontece sozinha quando o trabalho em curso declara os arquivos que vai tocar — o produto do memox é chegar antes de alguém perguntar.

Os comandos existem para quando você quer perguntar mesmo assim.

### Comandos

| Comando | O que faz |
|---|---|
| `/memox` | estado do índice: quantos trabalhos, quando foi reconstruído, o que ficou de fora e por quê |
| `/memox-indexar` | reconstrói o índice do zero |
| `/memox-arquivo <caminho>` | o que se sabe sobre um arquivo |
| `/memox-modulo <nome>` | o que se sabe sobre uma área |
| `/memox-buscar <termo>` | busca textual em título, causa e resumo |

O motor por trás deles é `.claude/skills/memox/assets/memox.py`, chamável direto:

```bash
python3 .claude/skills/memox/assets/memox.py arquivo "src/frete/calculo.ts"
python3 .claude/skills/memox/assets/memox.py modulo "frete"
python3 .claude/skills/memox/assets/memox.py buscar "arredondamento"
python3 .claude/skills/memox/assets/memox.py trabalho "OC-2026-0142"
```

Opções: `--formato json` para consumo por outra skill; `--raiz <dir>` para consultar outro projeto.

---

## O que é indexado

| Fonte | O que se extrai |
|---|---|
| `docs/relatorios/*/tecnico.md` | trabalho, data de fechamento, tipo, módulo, arquivos alterados, causa em uma linha, risco residual |
| `docs/relatorios/INDICE.md` | a linha do tempo, para ordenação e contagem |
| `docs/manutencao/*/01-CAUSA-RAIZ.md` | modo, se a causa foi comprovada, arquivos impactados, decisões |
| `docs/<slug>/00-DECISOES.md` | cada decisão com a alternativa descartada e o motivo |
| `docs/legado/DIVIDA.md` | dívida observada por arquivo, com risco estimado |
| `base/00-LACUNAS.md` | o que a documentação não respondia |
| `docs/manutencao/*/QA.md` | reprovações — o sinal mais forte de área frágil |
| `docs/entregas/*/ENTREGA.md` | branch, commits e faixa de atenção por arquivo |

O índice tem quatro chaves: **por arquivo**, **por módulo**, **por decisão** e **por termo**.

Toda entrada guarda o caminho do artefato de origem e a data. Nada no índice existe sem apontar para um artefato real — o que torna o índice inteiro descartável e reconstruível do zero a qualquer momento.

---

## Os sinais derivados

Além de listar, o índice calcula por arquivo e por módulo: quantos trabalhos o tocaram, a data do trabalho mais recente, quantas vezes foi reprovado em QA, se está em zona de risco declarada, se tem dívida registrada, e a faixa de atenção mais frequente nas entregas.

### O sinal de regressão

É o mais valioso e o mais fácil de perder: é o que identifica **o arquivo que "sempre volta"**. Ele alimenta o cálculo de raio da `legadox`, que hoje só enxerga a estrutura do código — quem importa quem, quem chama o quê — e por isso não sabe o que já quebrou.

Dois arquivos com raio estrutural idêntico não têm o mesmo risco se um deles já causou duas regressões e o outro nunca falhou. Essa diferença não está no código; está nos artefatos.

Um trabalho **B** é registrado como regressão de um trabalho **A** apenas quando as três condições valem juntas:

1. um arquivo apontado pela causa raiz de B está entre os arquivos que A alterou;
2. a data de A é estritamente anterior à de B, e as duas datas existem;
3. B tem causa raiz **comprovada** — não análise de impacto, não hipótese.

Faltando qualquer uma, o vínculo é registrado como **coincidência de arquivo**, com o motivo explícito. Dois trabalhos tocando o mesmo arquivo é um fato; dizer que um causou o outro é uma afirmação, e afirmação exige evidência. Um arquivo central é tocado por dezenas de trabalhos sem relação causal entre eles — chamar isso de regressão transformaria o sinal mais valioso do índice em ruído.

Toda regressão registrada carrega os dois caminhos de artefato: o da causa raiz que aponta e o do relatório que alterou. Quem recebe o sinal pode abrir os dois e conferir.

---

## Controle de ruído

A parte que decide se isso é útil ou irritante. Arquivo muito tocado aparece em dezenas de trabalhos; injetar todos é pior que não injetar nada.

- no máximo **3 entradas recentes** por arquivo;
- **mais**, sempre e independentemente da data, as entradas com **regressão** ou **reprovação em QA** — a idade não as torna irrelevantes;
- acima de **8 entradas relevantes**, o memox não lista: informa a contagem e aponta o índice, deixando o humano decidir se abre.

E, quando não há nada relevante, **silêncio total**: nem uma linha dizendo que não achou. Ruído recorrente treina o time a ignorar, e um bloco que aparece sempre é pulado inteiro — inclusive na vez em que continha o aviso que importava.

Os limites ficam em `.expx/memoria/config.json`, que é do projeto: **a reconstrução do índice nunca o sobrescreve.**

---

## Hooks: a memória que não depende de o modelo lembrar

O índice é um arquivo — e arquivo depende de alguém lembrar de o consultar. Dois hooks fecham essa lacuna, e **nenhum dos dois bloqueia nada**: ambos saem com código 0 sempre, inclusive em erro.

| Hook | Quando | O que faz |
|---|---|---|
| `memox-injetar.sh` | ao enviar o prompt | detecta os arquivos e módulos que o prompt declara que serão tocados, consulta o índice e injeta o que se sabe, dentro dos limites de ruído e sempre com procedência |
| `memox-reindexar.sh` | ao fim da sessão | reconstrói o índice se algum artefato mudou |

A injeção roda **abaixo de 200 ms, sem rede e sem modelo**. Falha aberta é regra, não acidente: um índice quebrado nunca pode travar o prompt de quem está trabalhando.

---

## Integração com as outras camadas

| Camada | Onde entra |
|---|---|
| [`sprintx`](docs/integracao/patch-sprintx.md) | consulta na F1 e na F3, sobre os arquivos que o plano pretende tocar |
| [`runx`](docs/integracao/patch-runx.md) | consulta na E1, sobre os arquivos impactados da causa raiz; dispara reindexação na E5 |
| [`legadox`](docs/integracao/patch-legadox.md) | consome regressão e reprovação em QA como entrada do cálculo de raio |
| [`mergex`](docs/integracao/patch-mergex.md) | consulta na classificação de atenção: arquivo com histórico de regressão sobe de faixa |

Os patches em [`docs/integracao/`](docs/integracao/) são prompts autônomos que alteram cada skill. **Nenhum altera comportamento quando o memox não está instalado.**

A integração mais valiosa é a da `sprintx` com as decisões: cada decisão registrada guarda a alternativa que foi descartada e o motivo. Replanejar a alternativa já descartada, sem saber que foi descartada, é o desperdício mais caro e mais silencioso que um time comete.

---

## O que o memox NÃO faz

- **Não guarda conhecimento próprio.** Toda entrada aponta para um artefato real, com caminho e data. Não há uma "versão do memox" dos fatos que possa divergir dos artefatos e envelhecer em silêncio. Artefato errado se corrige no artefato, e o índice reflete na próxima reconstrução.
- **Não resume conversa.** Transcript não é fonte. O que entra no índice já passou por revisão humana.
- **Não usa embedding.** Sem banco vetorial, sem modelo na ingestão, sem modelo na consulta. Consulta é local e instantânea.
- **Não substitui ler o artefato.** A resposta é um ponteiro — trabalho, data, causa em uma linha e o caminho onde está o detalhe. A linha `ver:` é o produto, não decoração.
- **Não inventa relação.** Coincidência de arquivo não vira regressão por parecer plausível.
- **Não edita artefato.** O memox só lê.
- **Não injeta segredo.** Detectado um segredo num artefato, o trecho é omitido do índice e o artefato é reportado como contaminado.

---

## Estrutura em disco

Tudo que o memox produz no projeto:

```
.expx/memoria/
  indice.json         o índice invertido, derivado e reconstruível
  config.json         os limites de ruído e as fontes — do projeto, nunca sobrescrito
```

A pasta inteira é derivada: pode ser apagada a qualquer momento e reconstruída com `/memox-indexar`. Por isso ela **não é versionada** — o `.gitignore` já a exclui.

---

## Estrutura do repositório

```
.claude/
  skills/memox/
    SKILL.md                    identidade, arquitetura, sinais, regras invioláveis
    DECISOES-DA-SKILL.md        as decisões de desenho e as alternativas descartadas
    references/                 roteiro detalhado de indexação, sinais, consulta, injeção e manutenção
    assets/
      memox.py                  o motor: Python 3, só biblioteca padrão
      TEMPLATE-*.md             formato do índice e da configuração
  commands/memox*.md            os comandos do Claude Code
  hooks/memox-*.sh              a injeção e a reindexação
.opencode/
  commands/memox*.md            os mesmos comandos, no formato do OpenCode
docs/integracao/                os patches para colar em cada skill irmã
exemplos/                       um índice e uma consulta preenchidos
assets/                         diagrama de fluxo do README
.github/assets/                 banner e badges do README
AGENTS.md                       instruções de acionamento para o agente
```

O `SKILL.md` é a porta de entrada e fica enxuto. O detalhe operacional mora no `reference` correspondente, lido **só quando a etapa chega** — mantendo o contexto pequeno.

Exemplos de saída real em [`exemplos/`](exemplos/): um [índice preenchido](exemplos/indice.exemplo.json) e uma [consulta respondida](exemplos/consulta.exemplo.md).

---

## Licença

MIT. Veja [LICENSE](LICENSE).

---

## Como contribuir

Abra uma issue descrevendo o caso concreto — o repositório, a consulta e o que aconteceu — antes de abrir um PR grande.

Contribuição mais útil, em ordem:

1. **Fontes que faltam** — um artefato do método que o `references/01-indexacao.md` não lê, ou um campo de frontmatter que ele ignora.
2. **Ruído observado** — uma injeção que apareceu e não deveria. Ruído recorrente treina o time a ignorar o bloco inteiro; é o defeito mais caro desta skill.
3. **Regressão perdida ou inventada** — um vínculo causal que o índice deixou passar, ou uma coincidência de arquivo que ele promoveu a regressão.

As três condições da regra de regressão não se flexibilizam sem o caso de uso que justifique: elas existem porque um índice que chama coincidência de causa destrói o próprio sinal que o torna valioso.

---

<div align="center">
<sub>Parte do método <strong>Expx</strong> ·
<a href="https://github.com/bittencourtthulio/expxdev">expxdev</a> ·
<a href="https://github.com/bittencourtthulio/sprintx">sprintx</a> ·
<a href="https://github.com/bittencourtthulio/runx">runx</a> ·
<a href="https://github.com/bittencourtthulio/legadox">legadox</a> ·
<a href="https://github.com/bittencourtthulio/stackx">stackx</a> ·
<a href="https://github.com/bittencourtthulio/mergex">mergex</a> ·
memox</sub>
</div>
