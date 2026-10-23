import importlib.util
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
MOTOR = ROOT / ".claude" / "skills" / "memox" / "assets" / "memox.py"
SPEC = importlib.util.spec_from_file_location("memox", MOTOR)
memox = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(memox)


def escrever(caminho, conteudo):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8")


class MemoxRegressoesTest(unittest.TestCase):
    def test_raiz_projeto_reconhece_git_file_de_worktree(self):
        with TemporaryDirectory() as tmp:
            raiz = Path(tmp) / "worktree"
            fundo = raiz / "src" / "modulo"
            fundo.mkdir(parents=True)
            (raiz / ".git").write_text("gitdir: /tmp/repositorio/worktrees/x\n")
            self.assertEqual(memox.raiz_projeto(str(fundo)), str(raiz))

    def test_config_descarta_json_de_tipo_incompativel(self):
        with TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            config = raiz / ".expx" / "memoria" / "config.json"
            escrever(config, "[]")
            self.assertEqual(memox.carregar_config(str(raiz)), memox.CONFIG_PADRAO)

            escrever(config, '{"fontes": null, "ignorar": "dist", "teto_entradas": true}')
            carregada = memox.carregar_config(str(raiz))
            self.assertEqual(carregada["fontes"], memox.CONFIG_PADRAO["fontes"])
            self.assertEqual(carregada["ignorar"], memox.CONFIG_PADRAO["ignorar"])
            self.assertEqual(carregada["teto_entradas"], memox.CONFIG_PADRAO["teto_entradas"])

    def test_redigir_remove_bloco_pem_inteiro(self):
        corpo = (
            "antes\n-----BEGIN PRIVATE KEY-----\n"
            "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo=\n"
            "c2VndW5kYS1saW5oYS1zZWNyZXRh\n"
            "-----END PRIVATE KEY-----\ndepois"
        )
        redigido, tipos = memox.redigir(corpo)
        self.assertIn("chave_privada", tipos)
        self.assertEqual(redigido, "antes\n[redigido pelo memox]\ndepois")
        self.assertNotIn("QUJD", redigido)
        self.assertNotIn("END PRIVATE KEY", redigido)

    def test_fechamento_e_qa_preservam_proveniencia_e_detalhes(self):
        with TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            trabalho = raiz / "docs" / "sprintx" / "features" / "pagamento"
            escrever(
                trabalho / "ORQUESTRADOR.md",
                """---
trabalho_id: FX-1
titulo: Pagamento
tipo_trabalho: feature
expx_tool: sprintx
---
Contexto do trabalho.
""",
            )
            escrever(
                trabalho / "FECHAMENTO.md",
                """---
trabalho_id: FX-1
titulo: Pagamento
tipo_trabalho: feature
expx_tool: sprintx
fechado_em: 2026-10-20
modulo_afetado: [pagamentos]
arquivos_alterados: [src/pagamento.py]
resumo: Fluxo de pagamento entregue por completo.
risco_residual: Nenhum risco residual conhecido.
---
Entrega final da feature.
""",
            )
            escrever(
                raiz / "docs" / "manutencao" / "FX-1" / "QA.md",
                """---
trabalho_id: FX-1
veredito: reprovado
executado_em: 2026-10-21
achados:
  - severidade: alta
    arquivo: src/pagamento.py
    problema: validacao ausente
---
VEREDITO: REPROVADO
""",
            )

            indice = memox.construir_indice(str(raiz), memox.CONFIG_PADRAO)
            entrada = indice["por_arquivo"]["src/pagamento.py"][0]
            self.assertTrue(entrada["artefato"].endswith("FECHAMENTO.md"))
            sinais = indice["sinais"]["modulo"]["pagamentos"]
            self.assertEqual(sinais["reprovacoes_qa"], 1)
            self.assertEqual(
                sinais["detalhe_reprovacoes"][0]["origem"],
                "docs/manutencao/FX-1/QA.md",
            )

    def test_gatilhos_acentuados_injetam_historico(self):
        indice = {
            "trabalhos": {"FX-1": {}},
            "por_arquivo": {
                "src/pagamento.py": [{
                    "trabalho_id": "FX-1",
                    "titulo": "Pagamento",
                    "data": "2026-10-20",
                    "tipo": "feature",
                    "causa": "Fluxo anterior",
                    "artefato": "docs/sprintx/features/pagamento/FECHAMENTO.md",
                }],
            },
            "por_modulo": {},
            "sinais": {"arquivo": {"src/pagamento.py": {}}, "modulo": {}},
            "config": memox.CONFIG_PADRAO,
        }
        texto = "Isso já aconteceu? Quero o histórico de src/pagamento.py."
        saida = memox.montar_injecao(indice, memox.CONFIG_PADRAO, texto)
        self.assertIn("memoria-expx", saida)
        self.assertIn("src/pagamento.py", saida)

    def test_exclusao_ou_renomeacao_dispara_reindexacao(self):
        with TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            fechamento = raiz / "docs" / "sprintx" / "features" / "x" / "FECHAMENTO.md"
            escrever(
                fechamento,
                """---
trabalho_id: FX-2
fechado_em: 2026-10-20
modulo_afetado: [x]
arquivos_alterados: [src/x.py]
---
Fechamento completo do trabalho.
""",
            )
            indice = memox.construir_indice(str(raiz), memox.CONFIG_PADRAO)
            memox.gravar_indice(str(raiz), indice)
            self.assertFalse(memox.precisa_reindexar(str(raiz), memox.CONFIG_PADRAO))

            renomeado = fechamento.with_name("FECHAMENTO-ANTIGO.md")
            fechamento.rename(renomeado)
            self.assertTrue(memox.precisa_reindexar(str(raiz), memox.CONFIG_PADRAO))

    def test_escrita_atomica_concorrente_nao_colide(self):
        with TemporaryDirectory() as tmp:
            destino = Path(tmp) / "indice.json"

            def gravar(n):
                memox._gravar_atomico(str(destino), json.dumps({"execucao": n}))

            with ThreadPoolExecutor(max_workers=8) as pool:
                list(pool.map(gravar, range(64)))

            final = json.loads(destino.read_text(encoding="utf-8"))
            self.assertIn(final["execucao"], range(64))
            self.assertEqual(list(Path(tmp).glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
