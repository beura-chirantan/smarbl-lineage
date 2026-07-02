"""Strict JSON boundary for the assignment's list-of-nodes format."""

from __future__ import annotations

import json
from pathlib import Path

from .errors import InputError
from .model import Node


def nodes_from_data(data: object) -> list[Node]:
    if not isinstance(data, list):
        raise InputError("JSON root must be an array of node objects")

    nodes: list[Node] = []
    required = ("id", "name", "expression")
    for index, item in enumerate(data):
        location = f"node at index {index}"
        if not isinstance(item, dict):
            raise InputError(f"{location} must be an object")

        missing = [field for field in required if field not in item]
        if missing:
            raise InputError(
                f"{location} is missing required field(s): {', '.join(missing)}"
            )

        try:
            node = Node(
                id=item["id"],
                name=item["name"],
                expression=item["expression"],
            )
        except (TypeError, ValueError) as exc:
            raise InputError(f"invalid {location}: {exc}") from exc
        nodes.append(node)

    return nodes


def load_nodes(path: str | Path) -> list[Node]:
    input_path = Path(path)
    try:
        with input_path.open("r", encoding="utf-8") as handle:
            data: object = json.load(handle)
    except json.JSONDecodeError as exc:
        raise InputError(
            f"invalid JSON in {input_path}: line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}"
        ) from exc
    except OSError as exc:
        raise InputError(f"cannot read {input_path}: {exc}") from exc

    return nodes_from_data(data)
