import unittest

from lineage import DependencyCache, LineageGraph, Node, PathFinder

from .fixtures import diamond_graph, sample_graph


class PathFinderTests(unittest.TestCase):
    def test_finds_assignment_direction_path(self) -> None:
        graph = sample_graph()
        paths = PathFinder(graph, DependencyCache(graph)).find_paths(
            "report-id", "price-id"
        )
        self.assertEqual(
            [[node.name for node in path] for path in paths],
            [["report", "margin", "revenue", "price"]],
        )

    def test_diamond_returns_both_distinct_paths_in_stable_order(self) -> None:
        graph = diamond_graph()
        paths = PathFinder(graph, DependencyCache(graph)).find_paths("a", "d")
        self.assertEqual(
            [[node.name for node in path] for path in paths],
            [["a", "b", "d"], ["a", "c", "d"]],
        )

    def test_wrong_direction_unknown_and_unreachable_are_empty(self) -> None:
        graph = sample_graph()
        finder = PathFinder(graph, DependencyCache(graph))
        self.assertEqual(finder.find_paths("price-id", "report-id"), [])
        self.assertEqual(finder.find_paths("missing", "report-id"), [])
        self.assertEqual(finder.find_paths("report-id", "missing"), [])
        self.assertEqual(finder.find_paths("price-id", "qty-id"), [])

    def test_same_endpoint_is_the_zero_edge_simple_path(self) -> None:
        graph = sample_graph()
        paths = PathFinder(graph).find_paths("report-id", "report-id")
        self.assertEqual([[node.id for node in path] for path in paths], [["report-id"]])

    def test_path_finder_enforces_simple_paths_even_without_cache(self) -> None:
        graph = LineageGraph(
            [
                Node("a", "a", "b + target"),
                Node("b", "b", "a + target"),
                Node("target", "target", "0"),
            ]
        )
        paths = PathFinder(graph).find_paths("a", "target")
        self.assertEqual(
            [[node.id for node in path] for path in paths],
            [["a", "b", "target"], ["a", "target"]],
        )
        for path in paths:
            self.assertEqual(len(path), len(set(path)))

    def test_pretty_output_includes_ids_and_arrows(self) -> None:
        graph = diamond_graph()
        paths = PathFinder(graph).find_paths("a", "d")
        rendered = PathFinder.prettify(paths)
        self.assertIn("1. a[a] -> b[b] -> d[d]", rendered)
        self.assertIn("2. a[a] -> c[c] -> d[d]", rendered)

    def test_iterative_search_handles_a_deep_path(self) -> None:
        size = 1_200
        graph = LineageGraph(
            [Node("0", "n0", "0")]
            + [
                Node(str(index), f"n{index}", f"n{index - 1}")
                for index in range(1, size)
            ]
        )
        paths = PathFinder(graph).find_paths(str(size - 1), "0")
        self.assertEqual(len(paths), 1)
        self.assertEqual(len(paths[0]), size)


if __name__ == "__main__":
    unittest.main()
