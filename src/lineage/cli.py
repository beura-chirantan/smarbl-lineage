"""Command-line query interface for JSON lineage files."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from collections.abc import Sequence, Set

try:
    # Importing readline enables arrow-key editing for input() on Unix/macOS.
    import readline as _readline
except ImportError:  # pragma: no cover - readline is not available on Windows.
    _readline = None

from .errors import LineageError
from .model import Node
from .service import LineageService


def _node_payload(node: Node) -> dict[str, str]:
    return {"id": node.id, "name": node.name, "expression": node.expression}


def _sorted_nodes(nodes: Set[Node]) -> list[Node]:
    return sorted(nodes, key=lambda node: (node.name, node.id))


def _add_json_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of formatted text",
    )


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lineage",
        description="Build and query a dependency graph from a JSON node list.",
    )
    parser.add_argument("input", help="path to the JSON array of nodes")
    commands = parser.add_subparsers(dest="command", required=True)

    summary = commands.add_parser("summary", help="show graph build statistics")
    _add_json_flag(summary)

    upstream = commands.add_parser(
        "upstream", help="list all direct and transitive dependencies"
    )
    upstream.add_argument("node_id")
    _add_json_flag(upstream)

    downstream = commands.add_parser(
        "downstream", help="list all nodes that directly or transitively use a node"
    )
    downstream.add_argument("node_id")
    _add_json_flag(downstream)

    paths = commands.add_parser(
        "paths", help="find every directed simple path between two node IDs"
    )
    paths.add_argument("from_id")
    paths.add_argument("to_id")
    _add_json_flag(paths)

    commands.add_parser(
        "shell",
        help="run many queries and reloads against one in-memory service",
    )

    return parser


def _print_node_set(nodes: Set[Node], as_json: bool) -> None:
    ordered = _sorted_nodes(nodes)
    if as_json:
        print(json.dumps([_node_payload(node) for node in ordered], indent=2))
        return
    if not ordered:
        print("No nodes found.")
        return
    for node in ordered:
        print(f"{node.id}\t{node.name}\t{node.expression}")


def _print_summary(service: LineageService, as_json: bool) -> None:
    graph = service.graph
    externals = {
        node.id: sorted(graph.external_references(node.id))
        for node in graph.nodes
        if graph.external_references(node.id)
    }
    payload = {
        "nodes": graph.node_count,
        "edges": graph.edge_count,
        "external_references": externals,
    }
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(f"Nodes: {payload['nodes']}")
    print(f"Dependency edges: {payload['edges']}")
    print(
        "Unresolved external names: "
        f"{sum(len(names) for names in externals.values())}"
    )


_SHELL_HELP = """Commands:
  summary [--json]
  upstream NODE_ID [--json]
  downstream NODE_ID [--json]
  paths FROM_ID TO_ID [--json]
  reload
  help
  exit
"""


def _remember_shell_command(line: str) -> None:
    """Add a command once so Up/Down can navigate this shell's history."""

    if _readline is None or not line.strip():
        return
    history_length = _readline.get_current_history_length()
    if (
        history_length == 0
        or _readline.get_history_item(history_length) != line
    ):
        _readline.add_history(line)


def _run_shell(service: LineageService) -> int:
    """Run many commands against one in-memory service snapshot."""

    print(
        f"Loaded {service.graph.node_count} nodes from {service.input_path}. "
        "Type 'help' for commands."
    )
    while True:
        try:
            line = input("lineage> ")
        except KeyboardInterrupt:
            print("\nCommand cancelled. Type 'exit' to quit.")
            continue
        except EOFError:
            print()
            return 0

        _remember_shell_command(line)

        try:
            parts = shlex.split(line)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            continue
        if not parts:
            continue

        command = parts.pop(0).lower()
        if command in {"exit", "quit"}:
            return 0
        if command == "help":
            print(_SHELL_HELP, end="")
            continue

        as_json = bool(parts and parts[-1] == "--json")
        if as_json:
            parts.pop()

        try:
            if command == "reload" and not parts and not as_json:
                service.reload()
                print(f"Reloaded {service.graph.node_count} nodes.")
            elif command == "summary" and not parts:
                _print_summary(service, as_json)
            elif command == "upstream" and len(parts) == 1:
                _print_node_set(service.get_upstream(parts[0]), as_json)
            elif command == "downstream" and len(parts) == 1:
                _print_node_set(service.get_downstream(parts[0]), as_json)
            elif command == "paths" and len(parts) == 2:
                found = service.find_paths(parts[0], parts[1])
                if as_json:
                    print(
                        json.dumps(
                            [
                                [_node_payload(node) for node in path]
                                for path in found
                            ],
                            indent=2,
                        )
                    )
                else:
                    print(service.path_finder.prettify(found))
            else:
                print(
                    "error: invalid shell command; type 'help' for usage",
                    file=sys.stderr,
                )
        except LineageError as exc:
            # A failed reload leaves the old snapshot active, so the shell can
            # report the problem and continue serving queries.
            print(f"error: {exc}", file=sys.stderr)
        except KeyboardInterrupt:
            print("\nCommand cancelled. Type 'exit' to quit.")


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)

    try:
        # The service owns one consistent graph/cache/path-finder snapshot.
        # Cache construction also validates cycles for every command, so an
        # invalid financial model never looks healthy.
        service = LineageService(args.input)

        if args.command == "shell":
            return _run_shell(service)

        if args.command == "summary":
            _print_summary(service, args.json)
            return 0

        if args.command == "upstream":
            _print_node_set(service.get_upstream(args.node_id), args.json)
            return 0

        if args.command == "downstream":
            _print_node_set(service.get_downstream(args.node_id), args.json)
            return 0

        finder = service.path_finder
        found = service.find_paths(args.from_id, args.to_id)
        if args.json:
            print(
                json.dumps(
                    [[_node_payload(node) for node in path] for path in found],
                    indent=2,
                )
            )
        else:
            print(finder.prettify(found))
        return 0
    except LineageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
