import unittest
from pathlib import Path

from src.rag_pipeline import load_documents, query, split_documents


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
        result = query(self.csv_path, "Qual é a anuidade do cartão Platinum?")
        self.assertEqual(result["reranked_candidates"], 8)
        self.assertEqual(result["reranked_selected"], 4)
        self.assertEqual(len(result["source_documents"]), 4)


if __name__ == "__main__":
    unittest.main()
