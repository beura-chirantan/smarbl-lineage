import unittest

from lineage import CycleError, DependencyCache, LineageGraph, Node

from .fixtures import diamond_graph, sample_graph


class DependencyCacheTests(unittest.TestCase):
    def test_assignment_upstream_example_and_downstream(self) -> None:
        graph = sample_graph()
        cache = DependencyCache(graph)
        self.assertEqual(
            {node.name for node in cache.get_upstream("report-id")},
            {"margin", "revenue", "cost", "price", "qty", "threshold"},
        )
        self.assertEqual(
            {node.name for node in cache.get_downstream("price-id")},
            {"revenue", "margin", "report"},
        )

    def test_diamond_closures_are_deduplicated(self) -> None:
        graph = diamond_graph()
        cache = DependencyCache(graph)
        self.assertEqual(
            {node.name for node in cache.get_upstream("a")}, {"b", "c", "d"}
        )
        self.assertEqual(
            {node.name for node in cache.get_downstream("d")}, {"a", "b", "c"}
        )

    def test_result_is_prebuilt_and_unknown_id_is_empty(self) -> None:
        graph = sample_graph()
        cache = DependencyCache(graph)
        first = cache.get_upstream("report-id")
        second = cache.get_upstream("report-id")
        self.assertIs(first, second)
        self.assertEqual(cache.get_upstream("missing"), set())
        self.assertEqual(cache.get_downstream(None), set())
        # collections.abc.Set mixins should preserve set semantics even though
        # the stored result has a compact custom representation.
        self.assertEqual(
            first & {graph.get_node("margin-id"), graph.get_node("price-id")},
            {graph.get_node("margin-id"), graph.get_node("price-id")},
        )
        self.assertEqual(first | set(), set(first))

    def test_start_node_is_excluded_from_its_closure(self) -> None:
        graph = diamond_graph()
        cache = DependencyCache(graph)
        self.assertNotIn(graph.get_node("a"), cache.get_upstream("a"))
        self.assertNotIn(graph.get_node("d"), cache.get_downstream("d"))

    def test_self_cycle_is_rejected_with_witness(self) -> None:
        graph = LineageGraph([Node("a", "a", "a")])
        with self.assertRaises(CycleError) as caught:
            DependencyCache(graph)
        self.assertEqual([node.id for node in caught.exception.cycle], ["a", "a"])

    def test_multi_node_cycle_in_disconnected_component_is_rejected(self) -> None:
        graph = LineageGraph(
            [
                Node("ok", "ok", "0"),
                Node("a", "a", "b"),
                Node("b", "b", "c"),
                Node("c", "c", "a"),
            ]
        )
        with self.assertRaisesRegex(CycleError, r"a\[a\].*b\[b\].*c\[c\].*a\[a\]"):
            DependencyCache(graph)

    def test_iterative_algorithm_handles_depth_above_recursion_limit(self) -> None:
        size = 1_200
        nodes = [Node("0", "n0", "0")]
        nodes.extend(
            Node(str(index), f"n{index}", f"n{index - 1}")
            for index in range(1, size)
        )
        cache = DependencyCache(LineageGraph(nodes))
        self.assertEqual(len(cache.get_upstream(str(size - 1))), size - 1)


if __name__ == "__main__":
    unittest.main()
