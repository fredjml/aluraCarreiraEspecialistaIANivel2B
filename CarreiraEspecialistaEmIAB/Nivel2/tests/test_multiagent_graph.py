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


if __name__ == "__main__":
    unittest.main()
