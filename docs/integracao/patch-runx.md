# Patch runx — consultar o memox na E1 e reindexar na E5

Prompt autônomo. Execute-o na raiz do repositório da skill `runx`. Trabalhe até o fim: não faça perguntas, não peça autorização, não pare no meio.

═══════════════════════════════════════════════════════════════════════
## PARTE 1 — CONTRATO
═══════════════════════════════════════════════════════════════════════

O `memox` é a camada de memória do ecossistema Expx. Ele indexa os artefatos já fechados e responde, com proveniência, o que se sabe sobre um arquivo ou módulo.

Este patch faz a `runx` **consumir** o memox na E1 (investigação), sobre os arquivos impactados da causa raiz, e **alimentar** o memox na E5 (relatório), disparando a reindexação ao fechar a ocorrência.

### O que este patch NÃO faz

- Não altera a máquina de estados E1→E5, nem os portões entre estágios.
- **Não relaxa a regra 2 da `runx`**: bug continua sem avançar da E1 sem causa raiz comprovada, com evidência própria desta ocorrência.
- Não altera o contrato da task, da fase ou da sprint, nem o `expx-schema v1`.
- Não altera comportamento quando o memox não está instalado.

### Contrato da consulta

```bash
python3 .claude/skills/memox/assets/memox.py arquivo "<caminho>" --formato json
```

Antes de consultar, verifique se `.claude/skills/memox/assets/memox.py` existe. Não existindo, **pule em silêncio** e siga o estágio.

═══════════════════════════════════════════════════════════════════════
## PARTE 2 — O QUE ALTERAR
═══════════════════════════════════════════════════════════════════════

### 2.1 — `references/01-investigacao.md` (E1)

Acrescente uma seção **Consulta à memória do projeto**, posicionada **depois** de `arquivos_impactados` existir e **antes** do fechamento de `01-CAUSA-RAIZ.md`.

Conteúdo a escrever:

- Consulte o memox para cada arquivo de `arquivos_impactados`.
- Se o memox não estiver instalado, pule em silêncio.
- O que fazer com cada sinal:

| Sinal do memox | Efeito na investigação |
|---|---|
| regressão registrada apontando para este arquivo | **verifique se esta ocorrência é outra recaída do mesmo ponto**; o artefato do trabalho anterior é leitura obrigatória antes de fechar a causa |
| trabalho anterior com causa raiz no mesmo arquivo | hipótese de partida, a ser comprovada como qualquer outra |
| reprovação em QA no arquivo | o ponto que reprovou entra nos passos de reprodução |
| decisão registrada sobre o módulo | confira se a correção pretendida não reverte uma decisão consciente; revertendo, registre a decisão |
| dívida ou zona de risco | material para o risco residual do relatório técnico da E5 |
| saída vazia | nada a registrar; não escreva "sem histórico" |

- **A regra que não pode ser quebrada**, escrita explicitamente na seção: o histórico é ponto de partida, nunca conclusão. Nenhuma quantidade de histórico substitui a prova exigida pela regra 2. Um arquivo que regrediu três vezes é um bom lugar para procurar, não uma causa comprovada. É proibido marcar `comprovada: true` com base em histórico do memox.
- Todo achado incorporado à investigação cita o caminho do artefato de origem.

### 2.2 — `references/05-relatorio.md` (E5)

Acrescente uma seção **Reindexação da memória**, como **último passo** do estágio, depois de gravar os dois relatórios e atualizar `docs/relatorios/INDICE.md`.

Conteúdo a escrever:

```bash
python3 .claude/skills/memox/assets/memox.py indexar
```

- Se o memox não estiver instalado, pule em silêncio.
- Se o hook `Stop` (`memox-reindexar.sh`) estiver registrado, ele já reconstrói sozinho; o disparo explícito existe para quem não instalou o hook e para deixar o índice pronto imediatamente — a ocorrência recém-fechada é a que tem mais chance de ser consultada em seguida.
- A reindexação **nunca** bloqueia o fechamento da ocorrência: falhando, a ocorrência fecha do mesmo jeito.
- Registre no relatório técnico, em uma linha, que a memória foi reindexada.

Ordem obrigatória: os relatórios e o `INDICE.md` **antes** da reindexação. O índice lê o que está em disco; reindexar antes de gravar não veria a ocorrência.

### 2.3 — `SKILL.md`

Na tabela de estágios → arquivos, indique que E1 consulta o memox e E5 dispara a reindexação, quando disponível. Uma linha. Registre o memox como dependência **opcional**, se houver seção para isso.

### 2.4 — `DECISOES-DA-SKILL.md`

Acrescente linhas registrando: a consulta na E1 e a reindexação na E5; a decisão de manter a regra 2 intacta (histórico nunca substitui prova); e a de manter tudo aditivo.

═══════════════════════════════════════════════════════════════════════
## PARTE 3 — VERIFICAÇÃO
═══════════════════════════════════════════════════════════════════════

1. `references/01-investigacao.md` tem a seção, posicionada após `arquivos_impactados` e antes de fechar a causa raiz.
2. A proibição de comprovar causa com base em histórico está escrita, explícita.
3. `references/05-relatorio.md` tem a reindexação como último passo, após os relatórios e o `INDICE.md`.
4. Ambas mandam pular em silêncio sem o memox.
5. Toda anotação exige o artefato de origem.
6. Nenhuma alteração no `expx-schema v1` nem nos contratos.
7. Simule uma E1 com o memox ausente: a investigação é idêntica à de antes do patch.
8. Simule uma E1 sobre arquivo com regressão registrada: o artefato anterior é citado, e `comprovada` continua exigindo evidência própria desta ocorrência.
9. Simule uma E5 com o memox ausente: a ocorrência fecha normalmente.
10. Simule uma E5 com a reindexação falhando: a ocorrência fecha do mesmo jeito.
11. Confirme que nada em `docs/manutencao/` é editado pelo memox (regra 12 da `runx`, regra 9 do memox).
12. Grep por caminho absoluto nos arquivos alterados: nenhum.

## ENTREGA

Mostre: os arquivos alterados com o diff de cada seção; o resultado das verificações 7 a 12; e as linhas acrescentadas ao `DECISOES-DA-SKILL.md`.
