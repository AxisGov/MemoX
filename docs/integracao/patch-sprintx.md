# Patch sprintx — consultar o memox na F1 e na F3

Prompt autônomo. Execute-o na raiz do repositório da skill `sprintx`. Trabalhe até o fim: não faça perguntas, não peça autorização, não pare no meio.

═══════════════════════════════════════════════════════════════════════
## PARTE 1 — CONTRATO
═══════════════════════════════════════════════════════════════════════

O `memox` é a camada de memória do ecossistema Expx. Ele indexa os artefatos já fechados — relatórios técnicos, causas raiz, decisões, dívida, lacunas, QA e entregas — e responde, com proveniência, o que se sabe sobre um arquivo ou módulo.

Este patch faz a `sprintx` **consultar** o memox em dois momentos: na F1 (ingestão), sobre as áreas da base; e na F3 (plano), sobre os arquivos que o plano pretende tocar.

### O que este patch NÃO faz

- Não altera a máquina de estados da `sprintx`, nem a ordem das fases.
- Não altera o contrato da task, da fase ou da sprint.
- Não altera o `expx-schema v1`.
- **Não altera comportamento quando o memox não está instalado.** A consulta é aditiva: se o motor não existe, falha ou devolve vazio, a fase segue exatamente como hoje.

### Contrato da consulta

```bash
python3 .claude/skills/memox/assets/memox.py arquivo "<caminho>" --formato json
python3 .claude/skills/memox/assets/memox.py modulo "<modulo>" --formato json
```

Local e instantânea: sem rede, sem modelo. Saída vazia significa "sem histórico indexado" — nunca "arquivo seguro".

### Detecção de disponibilidade

Antes de consultar, verifique se o arquivo `.claude/skills/memox/assets/memox.py` existe. Não existindo, **pule a consulta em silêncio** e siga a fase. Nenhuma mensagem de erro, nenhum aviso ao usuário: o memox é opcional.

═══════════════════════════════════════════════════════════════════════
## PARTE 2 — O QUE ALTERAR
═══════════════════════════════════════════════════════════════════════

### 2.1 — `references/01-ingestao.md` (F1)

Acrescente uma seção **Consulta à memória do projeto**, após o passo que identifica as áreas da base e antes do registro das lacunas.

Conteúdo a escrever:

- Para cada área identificada, consulte o memox por módulo; para cada arquivo já conhecido da área, consulte por arquivo.
- Se o memox não estiver instalado, pule esta seção em silêncio.
- O que fazer com cada sinal recebido:

| Sinal do memox | Efeito na F1 |
|---|---|
| regressão registrada | **lacuna a investigar**, com o artefato citado — não é conclusão, é ponto de partida |
| reprovação em QA | lacuna a investigar no ponto que reprovou |
| decisão registrada sobre o módulo | registrar na base como decisão vigente, com a alternativa descartada e o motivo |
| dívida ou zona de risco | registrar na base como contexto; não vira escopo |
| saída vazia | nada a registrar. **Não escreva "sem histórico"** — ausência de informação não é informação |

- Toda anotação vinda do memox cita o caminho do artefato de origem. Sem o caminho, a anotação não entra na base.
- O memox **não decide** o que é lacuna: ele fornece o fato, a `sprintx` classifica.

### 2.2 — `references/03-plano.md` (F3)

Acrescente uma seção **Verificação contra a memória do projeto**, após a consolidação da lista de arquivos que o plano vai tocar e **antes** de fechar as tasks.

Conteúdo a escrever:

- Consulte o memox para cada arquivo da lista consolidada.
- Efeitos obrigatórios no plano:

| Sinal | Efeito no plano |
|---|---|
| regressão registrada | task de teste cobrindo o caminho que regrediu; risco declarado no `riscos:` da sprint |
| reprovação em QA | critério de aceite mais estrito no ponto que reprovou |
| **decisão com alternativa descartada** | se o plano estiver adotando a alternativa já descartada, **pare e registre um `PENDENTE`** em `00-DECISOES.md`, citando a decisão anterior e seu motivo. Só siga adotando-a com justificativa explícita de por que agora é diferente |
| dívida registrada | risco declarado; a dívida **não** vira escopo de brinde |
| zona de risco | risco declarado no `riscos:` da sprint |

- O caso da decisão descartada é o mais valioso: replanejar uma alternativa que já foi avaliada e descartada, sem saber disso, é o desperdício mais caro e mais silencioso do ecossistema.
- Todo risco ou task originado do memox cita o artefato de origem no texto.

### 2.3 — `SKILL.md`

Na tabela de fases → arquivos, acrescente uma coluna ou nota indicando que F1 e F3 consultam o memox quando disponível. Uma linha, sem inflar o SKILL.md.

Se houver seção de dependências opcionais, registre o memox ali como **opcional**.

### 2.4 — `DECISOES-DA-SKILL.md`

Acrescente uma linha à tabela registrando este patch: a decisão de consultar o memox em F1 e F3, e a de manter a consulta estritamente aditiva (sem o memox, comportamento inalterado).

═══════════════════════════════════════════════════════════════════════
## PARTE 3 — VERIFICAÇÃO
═══════════════════════════════════════════════════════════════════════

1. `references/01-ingestao.md` tem a seção de consulta, posicionada antes do registro das lacunas.
2. `references/03-plano.md` tem a seção de verificação, posicionada antes do fechamento das tasks.
3. Ambas mandam pular em silêncio quando o memox não está instalado.
4. Ambas exigem citação do artefato de origem em toda anotação.
5. A regra da alternativa descartada está escrita, com o `PENDENTE` como consequência.
6. Nenhum arquivo do `expx-schema v1` foi alterado.
7. Nenhum contrato (task, fase, sprint) foi alterado.
8. Simule uma F3 com o memox ausente: o plano gerado é idêntico ao de antes do patch.
9. Simule uma F3 com o memox devolvendo vazio para todos os arquivos: o plano é idêntico, e **nenhuma** linha "sem histórico" foi escrita.
10. Simule uma F3 sobre um arquivo com regressão registrada: o plano tem a task de teste e o risco declarado, ambos citando o artefato.
11. Grep por caminho absoluto nos arquivos alterados: nenhum.

## ENTREGA

Mostre: os arquivos alterados com o diff de cada seção acrescentada; o resultado das verificações 8 a 11; e a linha acrescentada ao `DECISOES-DA-SKILL.md`.
