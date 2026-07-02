"""Reusable, reloadable owner of one immutable lineage snapshot."""

from __future__ import annotations

from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from .dependency_cache import DependencyCache
from .graph import LineageGraph
from .input import load_nodes
from .model import Node
from .path_finder import PathFinder


@dataclass(frozen=True, slots=True)
class _LineageSnapshot:
    """Objects that must always be replaced as one consistent unit."""

    graph: LineageGraph
    cache: DependencyCache
    path_finder: PathFinder


class LineageService:
    """Build once, answer many queries, and atomically reload changed input.

    Graphs and dependency caches are immutable, so a query can safely finish
    against the snapshot it started with while a successful reload publishes a
    new snapshot for later queries.
    """

    __slots__ = ("_input_path", "_lock", "_snapshot")

    def __init__(self, input_path: str | Path) -> None:
        self._input_path = Path(input_path)
        self._lock = Lock()
        self._snapshot = self._build_snapshot()

    @property
    def input_path(self) -> Path:
        return self._input_path

    def _build_snapshot(self) -> _LineageSnapshot:
        graph = LineageGraph(load_nodes(self._input_path))
        cache = DependencyCache(graph)
        return _LineageSnapshot(
            graph=graph,
            cache=cache,
            path_finder=PathFinder(graph, cache),
        )

    def _current_snapshot(self) -> _LineageSnapshot:
        with self._lock:
            return self._snapshot

    @property
    def graph(self) -> LineageGraph:
        return self._current_snapshot().graph

    @property
    def cache(self) -> DependencyCache:
        return self._current_snapshot().cache

    @property
    def path_finder(self) -> PathFinder:
        return self._current_snapshot().path_finder

    def reload(self) -> None:
        """Publish a newly validated snapshot built from the same input path.

        Construction happens before the swap. If loading, graph validation, or
        cycle validation fails, the exception is raised and the old valid
        snapshot remains available.
        """

        replacement = self._build_snapshot()
        with self._lock:
            self._snapshot = replacement

    def get_upstream(self, node_id: object) -> AbstractSet[Node]:
        snapshot = self._current_snapshot()
        return snapshot.cache.get_upstream(node_id)

    def get_downstream(self, node_id: object) -> AbstractSet[Node]:
        snapshot = self._current_snapshot()
        return snapshot.cache.get_downstream(node_id)

    def find_paths(self, from_id: object, to_id: object) -> list[list[Node]]:
        snapshot = self._current_snapshot()
        return snapshot.path_finder.find_paths(from_id, to_id)
