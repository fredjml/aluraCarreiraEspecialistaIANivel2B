import unittest
from pathlib import Path
from unittest.mock import patch

from src.evaluation import evaluate, summarize
from src.gemini_integration import JudgeDecision
from src.rag_pipeline import load_documents, query, split_documents


class FakeGemini:
    def answer_without_rag(self, question):
        return f"Resposta geral para: {question}"

    def rerank(self, question, candidates):
        return list(reversed(range(len(candidates))))

    def answer_with_rag(self, question, documents):
        return f"Resposta fundamentada [id={documents[0].metadata['id']}]"

    def judge(self, question, expected, answer, require_source):
        return JudgeDecision(True, 100, "resultado controlado do fake")


class RagPipelineTests(unittest.TestCase):
    csv_path = Path("data/politicas_bytebank.csv")

    def test_loads_all_fictitious_policies(self):
        documents = load_documents(self.csv_path)
        self.assertEqual(len(documents), 50)
        self.assertEqual(documents[0].metadata["id"], 1)
        self.assertIn("categoria_semantica", documents[0].metadata)

    def test_split_preserves_required_metadata(self):
        chunks = split_documents(load_documents(self.csv_path))
        self.assertGreaterEqual(len(chunks), 50)
        required = {"id", "dominio", "secao", "nivel_acesso", "categoria_semantica"}
        self.assertTrue(required.issubset(chunks[0].metadata))

    def test_query_returns_four_selected_sources(self):
        result = query(
            self.csv_path,
            "Qual é a anuidade do cartão Platinum?",
            llm_mode="local",
            retrieval_backend="lexical",
        )
        self.assertEqual(result["reranked_candidates"], 8)
        self.assertEqual(result["reranked_selected"], 4)
        self.assertEqual(len(result["source_documents"]), 4)
        self.assertEqual(result["mode"], "local_deterministic")

    def test_query_uses_gemini_for_reranking_and_generation(self):
        result = query(
            self.csv_path,
            "Qual é a anuidade do cartão Platinum?",
            llm_mode="gemini",
            gemini=FakeGemini(),
            retrieval_backend="lexical",
        )
        self.assertEqual(result["rerank_mode"], "gemini")
        self.assertEqual(result["generation_mode"], "gemini")
        self.assertEqual(result["fallbacks"], [])
        self.assertIn("[id=", result["answer"])

    def test_missing_key_uses_explicit_local_fallback(self):
        with patch(
            "src.rag_pipeline.GeminiIntegration.create_from_env",
            return_value=(None, "GOOGLE_API_KEY não configurada"),
        ):
            result = query(
                self.csv_path,
                "Qual o limite do Pix noturno?",
                llm_mode="gemini",
                retrieval_backend="lexical",
            )
        self.assertEqual(result["mode"], "local_deterministic")
        self.assertIn("GOOGLE_API_KEY não configurada", result["fallbacks"][0])

    def test_evaluation_compares_both_paths_and_records_judge(self):
        rows = evaluate(
            self.csv_path,
            llm_mode="gemini",
            gemini=FakeGemini(),
            retrieval_backend="lexical",
        )
        summary = summarize(rows)
        self.assertEqual(len(rows), 8)
        self.assertEqual(summary["acertos_sem_rag"], 8)
        self.assertEqual(summary["acertos_com_rag"], 8)
        self.assertTrue(all(row["modo_juiz"] == "gemini" for row in rows))

    def test_public_access_filter_excludes_internal_policies(self):
        result = query(
            self.csv_path,
            "Em quanto tempo vazamentos são comunicados à ANPD?",
            retrieval_backend="lexical",
        )
        self.assertTrue(
            all(
                document.metadata["nivel_acesso"] == "publico"
                for document in result["source_documents"]
            )
        )

    def test_vector_store_is_used_by_main_query(self):
        class FakeStore:
            def search(self, question, k, allowed_levels):
                documents = split_documents(load_documents(self_path))
                public = [d for d in documents if d.metadata["nivel_acesso"] == "publico"]
                return public[:k]

        self_path = self.csv_path
        result = query(
            self.csv_path,
            "Pix",
            retrieval_backend="chroma",
            vector_store=FakeStore(),
        )
        self.assertEqual(
            result["retrieval_mode"], "chroma_embeddings+lexical_hybrid"
        )
        self.assertEqual(result["allowed_levels"], ["publico"])


if __name__ == "__main__":
    unittest.main()
