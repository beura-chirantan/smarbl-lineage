"""Deterministic iterative enumeration of directed simple paths."""

from __future__ import annotations

from .dependency_cache import DependencyCache
from .graph import LineageGraph
from .model import Node


class PathFinder:
    def __init__(
        self,
        graph: LineageGraph,
        cache: DependencyCache | None = None,
    ) -> None:
        if cache is not None and cache.graph is not graph:
            raise ValueError("dependency cache belongs to a different graph")
        self._graph = graph
        self._cache = cache

    def find_paths(self, from_id: object, to_id: object) -> list[list[Node]]:
        source = self._graph.get_node(from_id)
        target = self._graph.get_node(to_id)
        if source is None or target is None:
            return []
        if source.id == target.id:
            return [[source]]
        if self._cache is not None and not self._cache.can_reach(
            source.id, target.id
        ):
            return []

        results: list[list[Node]] = []
        path_ids = [source.id]
        on_path = {source.id}
        # Frames are (current node ID, next neighbor index).
        stack: list[tuple[str, int]] = [(source.id, 0)]

        while stack:
            current_id, neighbor_index = stack[-1]
            neighbors = self._graph.dependency_ids(current_id)

            if neighbor_index >= len(neighbors):
                stack.pop()
                removed = path_ids.pop()
                on_path.remove(removed)
                continue

            next_id = neighbors[neighbor_index]
            stack[-1] = (current_id, neighbor_index + 1)

            if next_id in on_path:
                continue
            if (
                self._cache is not None
                and next_id != target.id
                and not self._cache.can_reach(next_id, target.id)
            ):
                continue

            path_ids.append(next_id)
            if next_id == target.id:
                results.append(
                    [
                        node
                        for node_id in path_ids
                        if (node := self._graph.get_node(node_id)) is not None
                    ]
                )
                path_ids.pop()
                continue

            on_path.add(next_id)
            stack.append((next_id, 0))

        return results

    @staticmethod
    def prettify(paths: list[list[Node]]) -> str:
        if not paths:
            return "No directed paths found."
        return "\n".join(
            f"{index}. "
            + " -> ".join(f"{node.name}[{node.id}]" for node in path)
            for index, path in enumerate(paths, start=1)
        )
