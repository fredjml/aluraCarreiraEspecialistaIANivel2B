import unittest

from scripts.bytebank_mcp_server import criar_conta, solicitar_cartao


class McpServerTests(unittest.TestCase):
    def test_mutations_require_human_approval(self):
        conta = criar_conta("cliente-ficticio")
        cartao = solicitar_cartao("cliente-ficticio", "Platinum")
        self.assertEqual(conta["status"], "human_approval_required")
        self.assertEqual(cartao["status"], "human_approval_required")


if __name__ == "__main__":
    unittest.main()
