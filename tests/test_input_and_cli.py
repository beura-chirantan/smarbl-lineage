import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from lineage import InputError
from lineage.cli import main
from lineage.input import load_nodes, nodes_from_data


class InputAndCliTests(unittest.TestCase):
    def test_numeric_ids_are_normalized_to_strings(self) -> None:
        nodes = nodes_from_data(
            [{"id": 123, "name": "node1", "expression": "0"}]
        )
        self.assertEqual(nodes[0].id, "123")

    def test_bad_shapes_and_field_types_are_rejected(self) -> None:
        bad_inputs = (
            {},
            ["not an object"],
            [{"id": "1", "name": "a"}],
            [{"id": True, "name": "a", "expression": "0"}],
            [{"id": "1", "name": "", "expression": "0"}],
            [{"id": "1", "name": "a", "expression": 0}],
        )
        for data in bad_inputs:
            with self.subTest(data=data), self.assertRaises(InputError):
                nodes_from_data(data)

    def test_non_identifier_name_is_allowed_but_cannot_be_referenced(self) -> None:
        nodes = nodes_from_data(
            [{"id": "1", "name": "display-only/name", "expression": "0"}]
        )
        self.assertEqual(nodes[0].name, "display-only/name")

    def test_malformed_json_has_line_and_column(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text("[{]", encoding="utf-8")
            with self.assertRaisesRegex(InputError, r"line 1, column"):
                load_nodes(path)

    def test_cli_summary_query_and_paths(self) -> None:
        data = [
            {"id": 1, "name": "base", "expression": "0"},
            {"id": 2, "name": "derived", "expression": "base"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nodes.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main([str(path), "summary", "--json"])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.getvalue())["edges"], 1)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main([str(path), "upstream", "2", "--json"])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.getvalue())[0]["id"], "1")

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main([str(path), "paths", "2", "1"])
            self.assertEqual(code, 0)
            self.assertIn("derived[2] -> base[1]", output.getvalue())

    def test_cli_reports_cycle_as_expected_error(self) -> None:
        data = [
            {"id": "a", "name": "a", "expression": "b"},
            {"id": "b", "name": "b", "expression": "a"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cycle.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                code = main([str(path), "summary"])
            self.assertEqual(code, 2)
            self.assertIn("cycle", errors.getvalue())

    def test_cli_shell_reuses_service_and_can_reload_changed_json(self) -> None:
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
            path.write_text(json.dumps(initial), encoding="utf-8")
            commands = iter(("summary", "reload", "upstream report", "exit"))

            def next_command(_prompt: str) -> str:
                command = next(commands)
                if command == "reload":
                    path.write_text(json.dumps(changed), encoding="utf-8")
                return command

            output = io.StringIO()
            with (
                mock.patch("builtins.input", side_effect=next_command),
                contextlib.redirect_stdout(output),
            ):
                code = main([str(path), "shell"])

            self.assertEqual(code, 0)
            self.assertIn("Loaded 2 nodes", output.getvalue())
            self.assertIn("Reloaded 3 nodes", output.getvalue())
            self.assertIn("derived", output.getvalue())
            self.assertIn("base", output.getvalue())

    def test_cli_shell_failed_reload_keeps_serving_previous_snapshot(self) -> None:
        initial = [
            {"id": "base", "name": "base", "expression": "0"},
            {"id": "derived", "name": "derived", "expression": "base"},
        ]
        cyclic = [
            {"id": "a", "name": "a", "expression": "b"},
            {"id": "b", "name": "b", "expression": "a"},
        ]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nodes.json"
            path.write_text(json.dumps(initial), encoding="utf-8")
            commands = iter(("reload", "upstream derived", "exit"))

            def next_command(_prompt: str) -> str:
                command = next(commands)
                if command == "reload":
                    path.write_text(json.dumps(cyclic), encoding="utf-8")
                return command

            output = io.StringIO()
            errors = io.StringIO()
            with (
                mock.patch("builtins.input", side_effect=next_command),
                contextlib.redirect_stdout(output),
                contextlib.redirect_stderr(errors),
            ):
                code = main([str(path), "shell"])

            self.assertEqual(code, 0)
            self.assertIn("cycle", errors.getvalue())
            self.assertIn("base", output.getvalue())

    def test_cli_shell_ctrl_c_cancels_without_exiting_or_traceback(self) -> None:
        data = [{"id": "base", "name": "base", "expression": "0"}]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nodes.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            output = io.StringIO()
            with (
                mock.patch(
                    "builtins.input",
                    side_effect=(KeyboardInterrupt(), "summary", "exit"),
                ),
                contextlib.redirect_stdout(output),
            ):
                code = main([str(path), "shell"])

            self.assertEqual(code, 0)
            self.assertIn("Command cancelled", output.getvalue())
            self.assertIn("Nodes: 1", output.getvalue())


if __name__ == "__main__":
    unittest.main()
