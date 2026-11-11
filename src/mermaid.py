"""Текст графа зависимостей на языке диаграмм Mermaid."""

import re

UNSAFE_ID = re.compile(r"[^A-Za-z0-9_]")


def mermaid_id(name: str, used: dict[str, str]) -> str:
    """Делает безопасный идентификатор узла Mermaid."""
    if name in used:
        return used[name]
    base = UNSAFE_ID.sub("_", name)
    if not base or base[0].isdigit():
        base = f"p_{base}"
    candidate = base
    taken = set(used.values())
    index = 2
    while candidate in taken:
        candidate = f"{base}_{index}"
        index += 1
    used[name] = candidate
    return candidate


def _label(name: str) -> str:
    """Экранирует имя пакета для подписи узла."""
    return name.replace('"', "'")


def to_mermaid(adjacency: dict[str, list[str]]) -> str:
    """Собирает описание графа в синтаксисе Mermaid."""
    used: dict[str, str] = {}
    nodes: list[str] = []
    for src, dests in adjacency.items():
        if src not in nodes:
            nodes.append(src)
        for dst in dests:
            if dst not in nodes:
                nodes.append(dst)
    lines = ["graph LR"]
    if not nodes:
        return "graph LR"
    for name in nodes:
        node = mermaid_id(name, used)
        lines.append(f'  {node}["{_label(name)}"]')
    seen: set[tuple[str, str]] = set()
    for src, dests in adjacency.items():
        for dst in dests:
            edge = (src, dst)
            if edge in seen:
                continue
            seen.add(edge)
            left = mermaid_id(src, used)
            right = mermaid_id(dst, used)
            lines.append(f"  {left} --> {right}")
    return "\n".join(lines)
