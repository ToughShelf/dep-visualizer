"""Юнит-тесты текста Mermaid."""

import unittest

from src.mermaid import to_mermaid


class TestMermaid(unittest.TestCase):
    """Проверяет описание графа на языке Mermaid."""

    def test_diamond(self) -> None:
        """Ромб превращается в рёбра Mermaid."""
        text = to_mermaid({
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        })
        self.assertTrue(text.startswith("graph LR"))
        self.assertIn('A["A"]', text)
        self.assertIn("A --> B", text)
        self.assertIn("C --> D", text)

    def test_hyphen_in_name(self) -> None:
        """Дефис в имени не попадает в идентификатор узла."""
        text = to_mermaid({"importlib-metadata": ["zipp"]})
        self.assertIn("importlib_metadata[", text)
        self.assertIn('["importlib-metadata"]', text)
        self.assertIn("importlib_metadata --> zipp", text)

    def test_cycle_edge(self) -> None:
        """Циклическое ребро остаётся в диаграмме."""
        text = to_mermaid({"A": ["A"]})
        self.assertIn("A --> A", text)

    def test_empty(self) -> None:
        """Пустой граф — заголовок без узлов."""
        self.assertEqual(to_mermaid({}), "graph LR")


if __name__ == "__main__":
    unittest.main()
