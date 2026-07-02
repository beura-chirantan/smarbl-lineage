import json
from pathlib import Path
import tempfile
import unittest

from lineage import (
    CycleError,
    GraphBuildError,
    GraphValidationError,
    InputError,
    LineageService,
)


class LineageServiceTests(unittest.TestCase):
    @staticmethod
    def _write(path: Path, data: list[dict[str, object]]) -> None:
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_queries_reuse_one_snapshot_and_reload_changed_json(self) -> None:
        initial = [
            {"id": "base", "name": "base", "expression": "0"},
            {"id": "derived", "name": "derived", "expression": "base"},
        ]
        changed = [
            *initial,
            {"id": "report", "name": "report", "expression": "derived"},
        ]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nodes.json"
            self._write(path, initial)
            service = LineageService(path)

            original_graph = service.graph
            original_cache = service.cache
            original_finder = service.path_finder

            self.assertEqual(
                {node.id for node in service.get_upstream("derived")},
                {"base"},
            )
            self.assertEqual(
                [[node.id for node in path] for path in service.find_paths(
                    "derived", "base"
                )],
                [["derived", "base"]],
            )
            self.assertIs(service.graph, original_graph)
            self.assertIs(service.cache, original_cache)
            self.assertIs(service.path_finder, original_finder)

            self._write(path, changed)
            service.reload()

            self.assertIsNot(service.graph, original_graph)
            self.assertIsNot(service.cache, original_cache)
            self.assertIsNot(service.path_finder, original_finder)
            self.assertEqual(service.graph.node_count, 3)
            self.assertEqual(
                {node.id for node in service.get_upstream("report")},
                {"base", "derived"},
            )

    def test_every_failed_reload_keeps_previous_valid_snapshot(self) -> None:
        initial = [
            {"id": "base", "name": "base", "expression": "0"},
            {"id": "derived", "name": "derived", "expression": "base"},
        ]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nodes.json"
            self._write(path, initial)
            service = LineageService(path)
            original_graph = service.graph
            original_cache = service.cache
            original_finder = service.path_finder

            failures = (
                ("malformed JSON", "[{]", InputError),
                (
                    "invalid expression",
                    json.dumps(
                        [
                            {"id": "base", "name": "base", "expression": "0"},
                            {
                                "id": "derived",
                                "name": "derived",
                                "expression": "base +",
                            },
                        ]
                    ),
                    GraphBuildError,
                ),
                (
                    "duplicate ID",
                    json.dumps(
                        [
                            {"id": "same", "name": "a", "expression": "0"},
                            {"id": "same", "name": "b", "expression": "0"},
                        ]
                    ),
                    GraphValidationError,
                ),
                (
                    "dependency cycle",
                    json.dumps(
                        [
                            {"id": "a", "name": "a", "expression": "b"},
                            {"id": "b", "name": "b", "expression": "a"},
                        ]
                    ),
                    CycleError,
                ),
            )

            for label, contents, error_type in failures:
                with self.subTest(label=label):
                    path.write_text(contents, encoding="utf-8")
                    with self.assertRaises(error_type):
                        service.reload()

                    self.assertIs(service.graph, original_graph)
                    self.assertIs(service.cache, original_cache)
                    self.assertIs(service.path_finder, original_finder)
                    self.assertEqual(
                        {node.id for node in service.get_upstream("derived")},
                        {"base"},
                    )


if __name__ == "__main__":
    unittest.main()
