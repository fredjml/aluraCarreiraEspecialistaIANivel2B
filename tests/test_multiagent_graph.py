import unittest

from src.multiagent_graph import build_graph


class MultiagentGraphTests(unittest.TestCase):
    def test_routes_three_domains(self):
        app = build_graph()
        cases = {
            "Como faço um Pix?": "conta_corrente",
            "Qual a anuidade do cartão?": "cartao_credito",
            "Qual o telefone do suporte?": "suporte",
        }
        for message, expected in cases.items():
            result = app.invoke({"mensagem": message})
            self.assertEqual(result["classificacao"], expected)
            self.assertIn(expected, result["resposta_final"])

    def test_uses_llm_classifier_when_provided(self):
        class FakeGemini:
            def classify_intent(self, message):
                return "suporte"

        app = build_graph(llm_mode="gemini", gemini=FakeGemini())
        result = app.invoke({"mensagem": "Preciso de ajuda com uma cobrança"})
        self.assertEqual(result["classificacao"], "suporte")
        self.assertEqual(result["modo_classificacao"], "gemini")

    def test_platinum_requires_human_approval(self):
        app = build_graph()
        result = app.invoke({"mensagem": "Quero solicitar cartão Platinum"})
        self.assertTrue(result["requer_aprovacao_humana"])
        self.assertIn("HITL", result["resposta_final"])

    def test_llm_failure_is_traced_and_falls_back(self):
        class FailingGemini:
            def classify_intent(self, message):
                raise RuntimeError("falha simulada")

        app = build_graph(llm_mode="gemini", gemini=FailingGemini())
        result = app.invoke({"mensagem": "Como faço um Pix?"})
        self.assertEqual(result["classificacao"], "conta_corrente")
        self.assertEqual(result["modo_classificacao"], "local_deterministic")
        self.assertIn("falha simulada", result["fallbacks"][0])


if __name__ == "__main__":
    unittest.main()
