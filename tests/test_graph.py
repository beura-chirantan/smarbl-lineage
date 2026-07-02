import unittest

from lineage import (
    GraphBuildError,
    GraphValidationError,
    LineageGraph,
    Node,
)

from .fixtures import sample_graph


class LineageGraphTests(unittest.TestCase):
    def test_builds_both_edge_directions_by_name(self) -> None:
        graph = sample_graph()
        self.assertEqual(
            {node.name for node in graph.get_uses("revenue-id")},
            {"price", "qty"},
        )
        self.assertEqual(
            {node.name for node in graph.get_used_by("revenue-id")},
            {"margin"},
        )
        self.assertEqual(graph.edge_count, 6)

    def test_external_names_are_skipped_but_observable(self) -> None:
        graph = LineageGraph([Node("a-id", "a", "external_rate + 1")])
        self.assertEqual(graph.get_uses("a-id"), set())
        self.assertEqual(graph.external_references("a-id"), {"external_rate"})

    def test_duplicate_references_create_only_one_edge(self) -> None:
        graph = LineageGraph(
            [Node("x", "x", "0"), Node("a", "a", "x + x * x")]
        )
        self.assertEqual(graph.edge_count, 1)
        self.assertEqual(graph.dependency_ids("a"), ("x",))

    def test_unknown_node_has_empty_neighbors(self) -> None:
        graph = sample_graph()
        self.assertEqual(graph.get_uses("missing"), set())
        self.assertEqual(graph.get_used_by(None), set())

    def test_duplicate_ids_and_names_are_rejected(self) -> None:
        with self.assertRaisesRegex(GraphValidationError, "duplicate node id"):
            LineageGraph([Node(123, "a", "0"), Node("123", "b", "0")])
        with self.assertRaisesRegex(GraphValidationError, "duplicate node name"):
            LineageGraph([Node("1", "same", "0"), Node("2", "same", "0")])

    def test_all_expression_failures_are_aggregated_atomically(self) -> None:
        with self.assertRaises(GraphBuildError) as caught:
            LineageGraph(
                [Node("a", "a", "a +"), Node("b", "b", "if (b")]
            )
        self.assertEqual(len(caught.exception.failures), 2)
        self.assertIn("node 'a'", str(caught.exception))
        self.assertIn("node 'b'", str(caught.exception))

    def test_input_order_does_not_affect_name_resolution(self) -> None:
        graph = LineageGraph(
            [Node("derived-id", "derived", "base"), Node("base-id", "base", "0")]
        )
        self.assertEqual(
            {node.id for node in graph.dependencies_of("derived-id")},
            {"base-id"},
        )


if __name__ == "__main__":
    unittest.main()
