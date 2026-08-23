import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class McpToolsIntegrationTests(unittest.TestCase):
    def test_json_protocol_over_stdin_stdout(self):
        requests = [
            {"operation": "list"},
            {"operation": "call_tool", "name": "criar_conta"},
            {"operation": "read_resource", "name": "consultar_saldo"},
            {"operation": "unknown"},
        ]
        payload = "".join(json.dumps(item) + "\n" for item in requests)

        result = subprocess.run(
            [sys.executable, "scripts/mcp_tools.py"],
            cwd=ROOT,
            input=payload,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        responses = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(len(responses), len(requests))
        self.assertIn("criar_conta", responses[0]["tools"])
        self.assertEqual(responses[1]["kind"], "mutation")
        self.assertEqual(responses[2]["kind"], "read")
        self.assertEqual(responses[3]["status"], "error")


if __name__ == "__main__":
    unittest.main()
