"""Teste de navegador opcional para a interface Gradio real."""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import unittest
from pathlib import Path


@unittest.skipUnless(os.getenv("BYTEBANK_RUN_BROWSER_E2E") == "1", "E2E Gradio não habilitado")
class GradioE2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.process = subprocess.Popen(
            [sys.executable, "-m", "src.app", "--port", "7861"],
            cwd=cls.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
                if connection.connect_ex(("127.0.0.1", 7861)) == 0:
                    return
            if cls.process.poll() is not None:
                output = cls.process.stdout.read() if cls.process.stdout else ""
                raise RuntimeError(f"servidor Gradio encerrou: {output}")
            time.sleep(0.25)
        cls.process.terminate()
        raise RuntimeError("servidor Gradio não abriu a porta 7861 em 20 segundos")

    @classmethod
    def tearDownClass(cls):
        if cls.process.poll() is None:
            cls.process.terminate()
            cls.process.wait(timeout=10)

    def test_question_displays_intent_and_response(self):
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto("http://127.0.0.1:7861", wait_until="networkidle")
            page.get_by_label("Pergunta").fill("Como faço um Pix?")
            page.get_by_role("button", name="Submit").click()
            intent = page.get_by_label("Intenção")
            intent.wait_for(state="visible")
            page.wait_for_function(
                "element => element.value === 'conta_corrente'",
                arg=intent.element_handle(),
            )
            self.assertEqual("conta_corrente", intent.input_value())
            browser.close()