#!/usr/bin/env bash
# memox-injetar.sh — hook UserPromptSubmit.
#
# Neste evento o stdout de texto simples e injetado no contexto do modelo.
# O hook detecta os arquivos e modulos que o prompt (ou o estado do projeto)
# declara que serao tocados, consulta o indice e injeta o que se sabe sobre
# eles, dentro dos limites de ruido e sempre com proveniencia.
#
# Contrato:
#   - silencioso quando nao ha nada relevante (regra 5);
#   - sai com 0 SEMPRE, inclusive em erro: falha aberta, nunca trava o prompt;
#   - abaixo de 200 ms; sem rede, sem modelo;
#   - inativo, sem erro, quando nao ha indice construido (DM-26).

set -u

# falha aberta: qualquer erro inesperado sai limpo
trap 'exit 0' ERR

ENTRADA=""
if [ ! -t 0 ]; then
  # leitura nao bloqueante do stdin do hook
  ENTRADA="$(timeout 1 cat 2>/dev/null || true)"
fi

# --- localiza a skill e a raiz do projeto ----------------------------------
DIR_HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMOX_PY="$DIR_HOOK/../skills/memox/assets/memox.py"
[ -f "$MEMOX_PY" ] || exit 0

PY="$(command -v python3 || true)"
[ -n "$PY" ] || exit 0

# raiz = repositorio git mais proximo do cwd; sem git, o cwd
if [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ -d "$CLAUDE_PROJECT_DIR" ]; then
  RAIZ="$(cd "$CLAUDE_PROJECT_DIR" && pwd)"
else
  RAIZ="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi

# --- inativo sem indice: nao existe memoria a injetar ----------------------
# O motor nunca indexa dentro deste hook; sem indice construido ele so devolveria
# silencio. Decidir pelo indice, e nao pelos caminhos padrao de docs/, faz o hook
# valer tambem quando `fontes` aponta outra arvore no config.json.
[ -f "$RAIZ/.expx/memoria/indice.json" ] || exit 0

# --- delega ao motor: extracao de alvos + consulta + limites de ruido ------
# Timeout duro: se por qualquer motivo passar de 2s, o prompt segue sem memoria.
printf '%s' "$ENTRADA" | timeout 2 "$PY" "$MEMOX_PY" injetar --raiz "$RAIZ" 2>/dev/null || true

exit 0
