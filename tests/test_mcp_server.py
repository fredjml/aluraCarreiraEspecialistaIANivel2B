import os
import unittest
from unittest.mock import patch

import jwt

from scripts.bytebank_mcp_server import consultar_politicas, criar_conta, solicitar_cartao


class McpServerTests(unittest.TestCase):
    jwt_environment = {
        "BYTEBANK_JWT_ISSUER": "https://identity.bytebank.local",
        "BYTEBANK_JWT_AUDIENCE": "bytebank-mcp",
        "BYTEBANK_JWT_SHARED_SECRET": "local-test-secret-with-at-least-thirty-two-characters",
        "BYTEBANK_JWT_ALGORITHMS": "HS256",
    }

    def _token(self, roles):
        payload = {
            "sub": "usuario-ficticio",
            "iss": self.jwt_environment["BYTEBANK_JWT_ISSUER"],
            "aud": self.jwt_environment["BYTEBANK_JWT_AUDIENCE"],
            "exp": 4_102_444_800,
            "roles": roles,
        }
        return jwt.encode(payload, self.jwt_environment["BYTEBANK_JWT_SHARED_SECRET"], algorithm="HS256")

    def test_mutations_require_approval_identity(self):
        conta = criar_conta("cliente-ficticio")
        cartao = solicitar_cartao("cliente-ficticio", "Platinum")
        self.assertEqual(conta["status"], "approval_identity_required")
        self.assertEqual(cartao["status"], "approval_identity_required")

    def test_mutation_requires_human_approval_after_identity_validation(self):
        with patch.dict(os.environ, self.jwt_environment, clear=False):
            result = criar_conta("cliente-ficticio", access_token=self._token(["aprovador"]))
        self.assertEqual(result["status"], "human_approval_required")

    def test_client_cannot_select_internal_access(self):
        result = consultar_politicas("vazamento ANPD")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["access_levels"], ["publico"])
        self.assertTrue(
            all(item["nivel_acesso"] == "publico" for item in result["source_documents"])
        )

    def test_invalid_token_is_denied(self):
        result = consultar_politicas("tarifa", access_token="token-invalido")
        self.assertEqual(result["status"], "unauthorized")

    def test_expired_token_is_denied(self):
        expired = jwt.encode(
            {
                "sub": "usuario-ficticio",
                "iss": self.jwt_environment["BYTEBANK_JWT_ISSUER"],
                "aud": self.jwt_environment["BYTEBANK_JWT_AUDIENCE"],
                "exp": 1,
                "roles": ["analista"],
            },
            self.jwt_environment["BYTEBANK_JWT_SHARED_SECRET"],
            algorithm="HS256",
        )
        with patch.dict(os.environ, self.jwt_environment, clear=False):
            result = consultar_politicas("tarifa", access_token=expired)
        self.assertEqual(result["status"], "unauthorized")

    def test_analyst_token_receives_internal_policy_access(self):
        with patch.dict(os.environ, self.jwt_environment, clear=False):
            result = consultar_politicas("vazamento ANPD", access_token=self._token(["analista"]))
        self.assertEqual(result["status"], "ok")
        self.assertIn("interno", result["access_levels"])


if __name__ == "__main__":
    unittest.main()
