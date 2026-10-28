"""Построение графа зависимостей обходом BFS с рекурсией."""

from collections.abc import Callable

NeighborFn = Callable[[str], list[str]]


def is_ancestor(node: str, other: str, parents: dict[str, str]) -> bool:
    """Проверяет, лежит ли other на пути BFS к node."""
    current = node
    seen: set[str] = set()
    while current in parents:
        if current in seen:
            return False
        seen.add(current)
        current = parents[current]
        if current == other:
            return True
    return False


def recursive_bfs(
    start: str,
    neighbors: NeighborFn,
) -> tuple[dict[str, list[str]], list[tuple[str, str]], list[str]]:
    """Строит граф BFS с рекурсией и находит циклы.

    Возвращает смежность, список циклических рёбер и порядок обхода.
    """
    adjacency: dict[str, list[str]] = {}
    cycles: list[tuple[str, str]] = []
    order: list[str] = []
    visited: set[str] = set()
    queued: set[str] = {start}
    parents: dict[str, str] = {}

    def bfs(queue: list[str]) -> None:
        if not queue:
            return
        name = queue.pop(0)
        queued.discard(name)
        if name in visited:
            bfs(queue)
            return
        visited.add(name)
        order.append(name)
        children = list(neighbors(name))
        adjacency[name] = children
        for child in children:
            cyclic = child == name or is_ancestor(name, child, parents)
            if cyclic:
                cycles.append((name, child))
                continue
            if child in visited or child in queued:
                continue
            parents[child] = name
            queued.add(child)
            queue.append(child)
        bfs(queue)

    bfs([start])
    return adjacency, cycles, order
