# Patch legadox — consumir regressão e reprovação em QA no cálculo de raio

Prompt autônomo. Execute-o na raiz do repositório da skill `legadox`. Trabalhe até o fim: não faça perguntas, não peça autorização, não pare no meio.

═══════════════════════════════════════════════════════════════════════
## PARTE 1 — CONTRATO
═══════════════════════════════════════════════════════════════════════

A `legadox` calcula o **raio de impacto** de uma mudança: o que mais pode quebrar quando se toca um ponto. Hoje o cálculo usa sinais **estruturais** — quem importa quem, quem chama o quê, o que compartilha tabela.

A estrutura responde "o que **pode** quebrar". Ela não sabe **o que já quebrou**. Dois arquivos com raio estrutural idêntico não têm o mesmo risco se um já causou duas regressões e o outro nunca falhou — e essa diferença não está no código, está nos artefatos.

Este patch faz a `legadox` consumir dois sinais do memox como **entrada do cálculo de raio**: regressão e reprovação em QA. É a integração de maior valor do memox, porque entrega informação que a `legadox` hoje não tem por nenhum outro meio.

### O que este patch NÃO faz

- Não altera o formato de `PERFIL.md` nem de `DIVIDA.md`.
- Não altera os sinais estruturais existentes nem seus pesos entre si.
- Não altera comportamento quando o memox não está instalado: o raio continua sendo calculado apenas com os sinais estruturais.

### Contrato da consulta

```bash
python3 .claude/skills/memox/assets/memox.py arquivo "<caminho>" --formato json
```

Do JSON, o campo `sinais`:

| Campo | Conteúdo |
|---|---|
| `regressoes` | lista; cada item com trabalho anterior, posterior, datas, evidência e os **dois** artefatos de origem |
| `reprovacoes_qa` | contagem; `detalhe_reprovacoes` traz trabalho, data e artefato |
| `zona_de_risco`, `divida`, `trabalhos`, `ultimo_trabalho_em`, `faixa_atencao_frequente` | complementares |

Antes de consultar, verifique se `.claude/skills/memox/assets/memox.py` existe. Não existindo, **pule em silêncio**.

═══════════════════════════════════════════════════════════════════════
## PARTE 2 — O QUE ALTERAR
═══════════════════════════════════════════════════════════════════════

### 2.1 — A reference do cálculo de raio

Acrescente uma seção **Sinais históricos**, ao lado da seção dos sinais estruturais.

Conteúdo a escrever:

- Para cada arquivo dentro do raio candidato, consulte o memox.
- `regressoes` não vazio e `reprovacoes_qa` alto **aumentam** o raio ou o peso do arquivo dentro dele. A ponderação exata é decisão da `legadox`; o memox fornece o fato.
- **Duas regras duras**, que precisam estar escritas na seção:

  1. **`coincidencias_arquivo` NÃO é sinal de regressão** e não entra no cálculo. Ela existe no índice para auditoria humana. Tratá-la como regressão infla o raio de todo arquivo central do sistema e destrói o valor do sinal. Se a `legadox` quiser usá-la, que seja como sinal próprio, com nome e peso próprios, **nunca somada às regressões**.
  2. **Ausência de sinal não reduz raio.** Arquivo sem histórico é arquivo sem informação, não arquivo seguro — um arquivo novo não tem histórico e nem por isso é seguro. O memox só acrescenta motivo para olhar mais; nunca subtrai.

- O campo `regressoes` já vem filtrado pelas três condições (vínculo por arquivo, ordem cronológica, causa comprovada). É evidência causal, não coincidência: pode ser consumido diretamente.

### 2.2 — O relatório de raio

Todo sinal histórico que alterou o raio precisa aparecer no relatório **com os dois artefatos de origem**:

```
src/frete/calculo.ts — raio elevado por historico
  regressao: OC-2026-0100 (2026-05-10) alterou o arquivo;
             OC-2026-0142 (2026-08-29) teve causa raiz comprovada apontando para ele.
    ver: docs/manutencao/OC-2026-0142-arredondamento/01-CAUSA-RAIZ.md
    ver: docs/relatorios/2026-05-10-OC-2026-0100-faixa-peso/tecnico.md
  reprovacoes em QA: 1
```

Sem os artefatos, a elevação de raio é uma afirmação não verificável — exatamente o que o método evita.

### 2.3 — Direção do fluxo

Documente, na reference: a `legadox` **consome** do memox e o **alimenta** pelos artefatos que já produz (`PERFIL.md` e `DIVIDA.md` são fontes indexadas). O ciclo se fecha pelos artefatos, não por chamada direta entre skills.

O memox não edita `PERFIL.md` nem `DIVIDA.md` (regra 9).

### 2.4 — `SKILL.md` e `DECISOES-DA-SKILL.md`

No `SKILL.md`, uma linha registrando o memox como fonte **opcional** de sinais históricos para o raio.

No `DECISOES-DA-SKILL.md`, registre: a decisão de consumir regressão e reprovação; a de **não** consumir coincidência de arquivo, e por quê; e a de que ausência de sinal não reduz raio.

═══════════════════════════════════════════════════════════════════════
## PARTE 3 — VERIFICAÇÃO
═══════════════════════════════════════════════════════════════════════

1. A reference do raio tem a seção de sinais históricos.
2. A proibição de consumir `coincidencias_arquivo` como regressão está escrita, com o motivo.
3. A regra "ausência de sinal não reduz raio" está escrita.
4. O relatório de raio exibe os dois artefatos de origem de cada regressão.
5. A seção manda pular em silêncio sem o memox.
6. Nenhuma alteração no formato de `PERFIL.md` ou `DIVIDA.md`.
7. Simule um cálculo com o memox ausente: o raio é idêntico ao de antes do patch.
8. Simule um arquivo com regressão registrada: o raio sobe e o relatório cita os dois artefatos.
9. Simule um arquivo que aparece apenas em `coincidencias_arquivo`: o raio **não** sobe por isso.
10. Simule um arquivo sem histórico: o raio **não** desce.
11. Grep por caminho absoluto nos arquivos alterados: nenhum.

## ENTREGA

Mostre: os arquivos alterados com o diff; o resultado das verificações 7 a 11; um exemplo de relatório de raio com sinal histórico e proveniência; e as linhas acrescentadas ao `DECISOES-DA-SKILL.md`.
