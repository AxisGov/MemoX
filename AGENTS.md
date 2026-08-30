# AGENTS.md — memox

Orientação para o agente do OpenCode neste repositório. O Claude Code lê a mesma informação por `.claude/skills/memox/SKILL.md`.

## O que é o memox

memox é a **camada de memória do método Expx** (Exponencial). As outras camadas produzem conhecimento — `sprintx` planeja features, `runx` trata ocorrências, `legadox` calcula raio de impacto, `stackx` descobre o dialeto do repositório, `mergex` versiona e entrega. Todas gravam artefatos em Markdown com frontmatter `expx-schema v1`.

O memox **não produz artefato novo**: ele indexa o que as outras já gravaram e devolve na hora certa. Como as demais camadas, não tem fluxo próprio.

## Princípio central

**Memória que precisa ser consultada não é usada.** O memox entrega o que se sabe sobre um arquivo no momento em que alguém declara que vai tocá-lo, sem ninguém pedir.

## Arquitetura: índice, não acervo semântico

O memox é um **índice invertido**. Sem embedding, sem banco vetorial, sem resumo de transcript, sem chamada de modelo na ingestão. Três motivos, que governam todo o desenho:

1. A pergunta real não é "o que é semanticamente parecido", é "quem já mexeu neste arquivo e por quê" — índice invertido, não busca vetorial.
2. Resposta de índice é verificável: aponta arquivo, trabalho e data. Recuperação semântica erra em silêncio.
3. Índice não custa nada por sessão e funciona desde o terceiro trabalho fechado.

Transcript de conversa **não é indexado**: contém o caminho descartado com a mesma aparência do adotado.

## Como usar neste repositório

O motor é `.claude/skills/memox/assets/memox.py` — Python 3, apenas biblioteca padrão.

```bash
python3 .claude/skills/memox/assets/memox.py estado
python3 .claude/skills/memox/assets/memox.py indexar
python3 .claude/skills/memox/assets/memox.py arquivo "src/frete/calculo.ts"
python3 .claude/skills/memox/assets/memox.py modulo "frete"
python3 .claude/skills/memox/assets/memox.py buscar "arredondamento"
python3 .claude/skills/memox/assets/memox.py trabalho "OC-2026-0142"
```

Opções: `--formato json` para consumo por outra skill; `--raiz <dir>` para consultar outro projeto.

Comandos equivalentes em `.opencode/commands/`: `/memox`, `/memox-indexar`, `/memox-arquivo`, `/memox-modulo`, `/memox-buscar`.

### Quando consultar sem o usuário pedir

Sempre que o trabalho em curso **declarar arquivos ou módulos que serão tocados** — plano de feature, causa raiz de ocorrência, cálculo de raio, classificação de faixa —, consulte o memox **antes** de escrever o plano. Depois do plano escrito, a informação de que o arquivo já regrediu custa retrabalho; antes, custa uma linha a mais no plano.

Também consulte quando a pergunta for sobre o passado: se algo já aconteceu, se é recorrente, quem mexeu num arquivo, o que já foi decidido sobre um módulo.

## Regras invioláveis

1. O memox não guarda conhecimento próprio. Toda entrada do índice aponta para um artefato real, com caminho e data.
2. O índice é derivado e descartável. Reconstruir do zero é sempre seguro.
3. Não indexa transcript de conversa, e não chama modelo para ingerir.
4. Não inventa relação. Se dois trabalhos tocaram o mesmo arquivo, isso é um fato; dizer que um causou o outro exige que a causa raiz do segundo aponte para o primeiro.
5. Silêncio quando não há nada relevante. Nunca injeta linha vazia.
6. Respeita os limites de ruído. Acima do teto, informa a contagem em vez de listar.
7. Nunca injeta segredo, credencial ou dado pessoal: se um artefato contiver, o índice registra o caminho e omite o trecho, e reporta o artefato como contaminado.
8. O índice é ignorado pelo versionador. Os artefatos é que são commitados.
9. O memox nunca edita artefato. Ele só lê.
10. Consulta é local e instantânea: sem rede, sem modelo, sem chamada externa.

Regra transversal: caminhos sempre relativos; nunca escreva caminho absoluto em nenhum artefato ou saída.

## Ao apresentar um resultado

- **Preserve a linha `ver:`.** Ela é o que separa uma resposta verificável de uma alegação. O memox não substitui ler o artefato; ele diz qual artefato ler.
- **Silêncio é resposta.** Consulta vazia significa que não há histórico indexado. Diga isso em uma linha e pare — não invente contexto, não especule.
- **Acima do teto, repasse a contagem.** Não tente listar em lotes: o teto existe porque injetar dezenas de entradas é pior que não injetar nada.
- **Nunca afirme causalidade a partir de coincidência.** Se o índice registrou `coincidencias_arquivo`, use a palavra *coincidência* e diga por que não é regressão.
- **Ausência de sinal não é atestado de segurança.** Arquivo sem histórico é arquivo sem informação.

## Estrutura do repositório

| Caminho | Conteúdo |
|---|---|
| `.claude/skills/memox/SKILL.md` | a skill (lida nativamente pelo OpenCode) |
| `.claude/skills/memox/references/` | roteiro operacional por etapa |
| `.claude/skills/memox/references/integracao/` | como cada camada consome o memox |
| `.claude/skills/memox/assets/memox.py` | o motor |
| `.claude/hooks/` | hooks do Claude Code (injeção e reindexação) |
| `.claude/commands/`, `.opencode/commands/` | os cinco comandos, idênticos |
| `docs/integracao/` | patches para as quatro skills |
| `exemplos/` | índice e consulta de exemplo |

**Skills ficam apenas em `.claude/skills/`.** Não crie `.opencode/skills/`: nomes de skill precisam ser únicos entre todas as localizações, e duplicar quebra a resolução.

## Lacuna declarada — hooks no OpenCode

Hooks são mecanismo do Claude Code. O OpenCode tem sistema próprio de eventos, ainda não mapeado para os dois hooks do memox. **Trate como lacuna a resolver, não como paridade garantida.**

Sem hook, o memox continua funcionando por consulta manual. A perda é a injeção automática — justamente o que diferencia memória disponível de memória usada. Enquanto isso, cabe ao agente consultar o memox por conta própria quando o trabalho declarar arquivos.
