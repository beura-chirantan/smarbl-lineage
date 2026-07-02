#!/usr/bin/env python3
"""Repeatable 10k-node construction/cache/path benchmark."""

from __future__ import annotations

import argparse
import gc
import os
import platform
import statistics
import time

from lineage import DependencyCache, LineageGraph, Node, PathFinder


def make_chain(size: int) -> list[Node]:
    width = len(str(size - 1))
    nodes = [Node("id-0", f"n{0:0{width}d}", "0")]
    for index in range(1, size):
        name = f"n{index:0{width}d}"
        dependency = f"n{index - 1:0{width}d}"
        nodes.append(Node(f"id-{index}", name, dependency))
    return nodes


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(len(ordered) * fraction + 0.999) - 1))
    return ordered[index]


def summarize(label: str, timings: list[float]) -> None:
    print(
        f"{label}: median={statistics.median(timings) * 1000:.2f} ms, "
        f"p95={percentile(timings, 0.95) * 1000:.2f} ms"
    )


def run(size: int, warmups: int, runs: int) -> None:
    nodes = make_chain(size)
    graph_times: list[float] = []
    cache_times: list[float] = []
    path_times: list[float] = []
    path_length = 0

    for iteration in range(warmups + runs):
        gc.collect()
        start = time.perf_counter()
        graph = LineageGraph(nodes)
        graph_done = time.perf_counter()
        cache = DependencyCache(graph)
        cache_done = time.perf_counter()
        paths = PathFinder(graph, cache).find_paths(
            f"id-{size - 1}", "id-0"
        )
        paths_done = time.perf_counter()

        if (
            graph.node_count != size
            or graph.edge_count != size - 1
            or len(cache.get_upstream(f"id-{size - 1}")) != size - 1
            or len(cache.get_downstream("id-0")) != size - 1
            or len(paths) != 1
            or len(paths[0]) != size
        ):
            raise RuntimeError("benchmark correctness check failed")
        path_length = len(paths[0])

        if iteration >= warmups:
            graph_times.append(graph_done - start)
            cache_times.append(cache_done - graph_done)
            path_times.append(paths_done - cache_done)

        del paths, cache, graph

    print("Smarbl lineage benchmark")
    print(f"Python: {platform.python_version()} ({platform.python_implementation()})")
    print(f"Platform: {platform.platform()}")
    print(f"CPU count: {os.cpu_count()}")
    print(
        f"Topology: directed chain, nodes={size}, edges={size - 1}, "
        f"returned_paths=1, path_length={path_length}"
    )
    print(f"Method: warmups={warmups}, measured_runs={runs}")
    summarize("Graph build (ANTLR parse + adjacency)", graph_times)
    summarize("Dependency cache (cycle check + both closures)", cache_times)
    summarize("Path finding (prebuilt graph/cache)", path_times)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", type=int, default=10_000)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--runs", type=int, default=20)
    args = parser.parse_args()
    if args.nodes < 1 or args.warmups < 0 or args.runs < 1:
        parser.error("nodes and runs must be positive; warmups cannot be negative")
    run(args.nodes, args.warmups, args.runs)


if __name__ == "__main__":
    main()
