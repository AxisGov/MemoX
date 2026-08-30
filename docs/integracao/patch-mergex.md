# Patch mergex — histórico de regressão sobe a faixa de atenção

Prompt autônomo. Execute-o na raiz do repositório da skill `mergex`. Trabalhe até o fim: não faça perguntas, não peça autorização, não pare no meio.

═══════════════════════════════════════════════════════════════════════
## PARTE 1 — CONTRATO
═══════════════════════════════════════════════════════════════════════

A `mergex` versiona, entrega e revisa pull requests, e classifica a **faixa de atenção** de uma entrega: quanto de revisão humana aquele conjunto de mudanças exige.

A classificação hoje olha para a mudança: quantos arquivos, quantas linhas, que tipo de código, se toca migração ou dado sensível. Isso descreve o **tamanho e a natureza** do diff.

O que o diff não conta é o **passado do arquivo**. Uma mudança de três linhas num arquivo que já causou duas regressões merece mais olhos que uma mudança de trinta linhas num arquivo que nunca falhou. O tamanho do diff não sabe disso; o índice sabe.

Este patch faz a `mergex` consultar o memox na classificação de atenção.

### O que este patch NÃO faz

- Não altera o formato de `ENTREGA.md` nem o fluxo de entrega.
- Não altera os critérios existentes de classificação.
- Não bloqueia PR, não aprova, não reprova.
- Não altera comportamento quando o memox não está instalado.

### Contrato da consulta

```bash
python3 .claude/skills/memox/assets/memox.py arquivo "<caminho>" --formato json
```

Antes de consultar, verifique se `.claude/skills/memox/assets/memox.py` existe. Não existindo, **pule em silêncio**.

═══════════════════════════════════════════════════════════════════════
## PARTE 2 — O QUE ALTERAR
═══════════════════════════════════════════════════════════════════════

### 2.1 — A reference da classificação de atenção

Acrescente uma seção **Histórico do arquivo**, após os critérios estruturais e antes da faixa final.

Conteúdo a escrever:

- Para cada arquivo do diff, consulte o memox.
- Efeitos sobre a faixa:

| Sinal | Efeito |
|---|---|
| `regressoes` não vazio | **sobe de faixa** |
| `reprovacoes_qa` alto | sobe de faixa |
| `zona_de_risco` presente | sobe de faixa |
| `divida` com risco alto | material para a nota de revisão |
| nenhum sinal | **faixa inalterada** |

Quanto sobe, e qual o teto, é decisão da `mergex`.

- **Regra dura, que precisa estar escrita**: a faixa **nunca desce** por causa do memox. Ausência de histórico é ausência de informação, não atestado de segurança — um arquivo novo não tem histórico e nem por isso é seguro. O memox só acrescenta motivo para olhar mais.

- **`coincidencias_arquivo` não sobe faixa.** Coincidência de arquivo é fato bruto sem evidência causal; usá-la subiria a faixa de todo arquivo central do sistema, e uma faixa que está sempre alta não classifica nada.

### 2.2 — Justificativa obrigatória

Toda subida de faixa causada pelo memox precisa aparecer no relatório de revisão **com o artefato**:

```
Faixa elevada para alta: src/frete/calculo.ts ja causou regressao.
  OC-2026-0100 (2026-05-10) alterou o arquivo;
  OC-2026-0142 (2026-08-29) teve causa raiz comprovada apontando para ele.
  ver: docs/manutencao/OC-2026-0142-arredondamento/01-CAUSA-RAIZ.md
```

Sem a justificativa, a subida de faixa vira burocracia inexplicada, e quem revisa aprende a ignorá-la. Com ela, o revisor sabe **onde** olhar — que é o ponto inteiro.

### 2.3 — Direção do fluxo

Documente que a `mergex` **consome** do memox e o **alimenta** pelos artefatos: `docs/entregas/*/ENTREGA.md` é fonte indexada, de onde sai o sinal `faixa_atencao_frequente`. Um arquivo que entra repetidamente em entregas de faixa alta acumula esse histórico, e o ciclo se fecha pelos artefatos.

Para o sinal existir, `ENTREGA.md` precisa ter a faixa por arquivo no frontmatter:

```yaml
faixa_atencao:
  - arquivo: src/frete/calculo.ts
    faixa: alta
```

Se a `mergex` ainda não grava esse campo, acrescente-o ao template de `ENTREGA.md` — é o único ponto deste patch que **escreve** artefato, e é a `mergex` quem escreve, não o memox.

### 2.4 — `SKILL.md` e `DECISOES-DA-SKILL.md`

No `SKILL.md`, uma linha registrando o memox como fonte **opcional** na classificação de atenção.

No `DECISOES-DA-SKILL.md`, registre: a regra de que histórico de regressão sobe a faixa; a de que a faixa nunca desce por ausência de sinal; a exclusão das coincidências; e a justificativa obrigatória com artefato.

═══════════════════════════════════════════════════════════════════════
## PARTE 3 — VERIFICAÇÃO
═══════════════════════════════════════════════════════════════════════

1. A reference da classificação tem a seção de histórico.
2. A regra "a faixa nunca desce" está escrita.
3. A exclusão de `coincidencias_arquivo` está escrita, com o motivo.
4. A justificativa com artefato é obrigatória em toda subida de faixa.
5. A seção manda pular em silêncio sem o memox.
6. `ENTREGA.md` tem `faixa_atencao` por arquivo no frontmatter.
7. Simule uma classificação com o memox ausente: a faixa é idêntica à de antes do patch.
8. Simule um arquivo com regressão registrada: a faixa sobe e a justificativa cita trabalho, data e artefato.
9. Simule um arquivo sem histórico: a faixa **não** desce.
10. Simule um arquivo presente apenas em `coincidencias_arquivo`: a faixa **não** sobe.
11. Grep por caminho absoluto nos arquivos alterados: nenhum.

## ENTREGA

Mostre: os arquivos alterados com o diff; o resultado das verificações 7 a 11; um exemplo de relatório com subida de faixa justificada; e as linhas acrescentadas ao `DECISOES-DA-SKILL.md`.
