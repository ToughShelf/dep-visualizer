"""Юнит-тесты BFS-графа и тестовых репозиториев."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src.graph import invert_adjacency, recursive_bfs
from src.repository import (
    RepoError,
    get_direct_dependencies,
    load_full_adjacency,
    parse_graph_text,
)
from src.visualizer import print_graph

REPO = Path(__file__).resolve().parent.parent / "repo"


def neighbors_of(
    adjacency: dict[str, list[str]],
):
    """Возвращает функцию соседей по готовому графу."""

    def neighbors(name: str) -> list[str]:
        if name not in adjacency:
            raise RepoError(f"пакет не найден: {name}")
        return list(adjacency[name])

    return neighbors


class TestParseGraph(unittest.TestCase):
    """Проверяет текстовое описание графа A-Z."""

    def test_tree_file(self) -> None:
        """Дерево A -> B, C читается из файла."""
        adj = load_full_adjacency(str(REPO / "graph_tree.txt"))
        self.assertEqual(sorted(adj["A"]), ["B", "C"])
        self.assertEqual(adj["B"], [])

    def test_simple_json_graph(self) -> None:
        """JSON {A: [B, C]} читается как граф."""
        adj = load_full_adjacency(str(REPO / "graph_simple.json"))
        self.assertEqual(sorted(adj["A"]), ["B", "C"])
        self.assertEqual(adj["D"], [])

    def test_rejects_lowercase(self) -> None:
        """Строчные имена в тестовом графе недопустимы."""
        with self.assertRaises(RepoError):
            parse_graph_text("A: b\n")


class TestRecursiveBfs(unittest.TestCase):
    """Проверяет BFS с рекурсией, транзитивность и циклы."""

    def test_tree(self) -> None:
        """Обход дерева посещает все узлы."""
        adj = {"A": ["B", "C"], "B": [], "C": []}
        graph, cycles, order = recursive_bfs("A", neighbors_of(adj))
        self.assertEqual(order, ["A", "B", "C"])
        self.assertEqual(graph["A"], ["B", "C"])
        self.assertEqual(cycles, [])

    def test_diamond_not_cycle(self) -> None:
        """Общий потомок D не считается циклом."""
        adj = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }
        graph, cycles, order = recursive_bfs("A", neighbors_of(adj))
        self.assertEqual(cycles, [])
        self.assertIn("D", order)
        self.assertEqual(graph["C"], ["D"])

    def test_cycle(self) -> None:
        """Цикл A -> B -> C -> A фиксируется и не зацикливает обход."""
        adj = {"A": ["B"], "B": ["C"], "C": ["A"]}
        graph, cycles, order = recursive_bfs("A", neighbors_of(adj))
        self.assertEqual(set(order), {"A", "B", "C"})
        self.assertEqual(cycles, [("C", "A")])
        self.assertEqual(graph["C"], ["A"])

    def test_self_loop(self) -> None:
        """Петля A -> A обрабатывается как цикл."""
        adj = {"A": ["A"]}
        _graph, cycles, order = recursive_bfs("A", neighbors_of(adj))
        self.assertEqual(order, ["A"])
        self.assertEqual(cycles, [("A", "A")])


class TestPrintGraph(unittest.TestCase):
    """Проверяет вывод транзитивного графа."""

    def test_print_cycle(self) -> None:
        """На экран попадают рёбра и циклы."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            print_graph("A", {"A": ["B"], "B": ["A"]}, [("B", "A")])
        text = buf.getvalue()
        self.assertIn("A -> B", text)
        self.assertIn("B -> A", text)
        self.assertIn("Циклические зависимости:", text)


class TestTestRepoDeps(unittest.TestCase):
    """Прямые зависимости из файлов графа."""

    def test_direct_from_letter_graph(self) -> None:
        """Тестовый граф отдаёт прямые зависимости A."""
        deps = get_direct_dependencies(
            "A",
            "1",
            str(REPO / "graph_diamond.txt"),
            True,
        )
        self.assertEqual(deps, ["B", "C"])


class TestInvert(unittest.TestCase):
    """Заготовка обратного графа для следующего этапа."""

    def test_invert_diamond(self) -> None:
        """У D появляются входящие B и C."""
        adj = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }
        reverse = invert_adjacency(adj)
        self.assertEqual(sorted(reverse["D"]), ["B", "C"])
        self.assertEqual(reverse["A"], [])


if __name__ == "__main__":
    unittest.main()
