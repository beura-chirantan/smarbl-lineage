# Expression Parser & Lineage Graph

Python 3.11+ implementation of the Smarbl take-home assignment. It parses
expressions with the supplied ANTLR4 grammar, builds an immutable bidirectional
dependency graph, precomputes upstream/downstream lineage, rejects cycles, and
finds every directed simple path between two nodes.

The generated ANTLR Python files are committed, so normal setup does not need
Java or the ANTLR generator.

## Quick start

```bash
bash setup.sh

bash run.sh examples/nodes.json summary
bash run.sh examples/nodes.json upstream report-id
bash run.sh examples/nodes.json downstream price-id
bash run.sh examples/nodes.json paths report-id price-id
```

`run.sh` directly uses `.venv/bin/python`, so activating the environment is
optional. To run Python commands manually:

```bash
source .venv/bin/activate
```

## Persistent shell

One-shot commands build one graph/cache snapshot, answer one query, and exit.
For repeated queries using the same snapshot:

```text
$ bash run.sh examples/nodes.json shell
lineage> summary
lineage> upstream report-id
lineage> downstream price-id
lineage> paths report-id price-id
lineage> exit
```

After editing the input JSON, enter `reload`. A successful reload replaces the
graph, cache, and path finder together. A failed reload reports the error and
keeps the previous valid snapshot.

On Unix and macOS, arrow keys provide command editing/history. `Ctrl+C` cancels
the current input or query without discarding the service.

## CLI reference

```text
bash run.sh INPUT summary [--json]
bash run.sh INPUT upstream NODE_ID [--json]
bash run.sh INPUT downstream NODE_ID [--json]
bash run.sh INPUT paths FROM_ID TO_ID [--json]
bash run.sh INPUT shell
```

- `summary`: node, edge, and unresolved-reference counts.
- `upstream`: all direct and transitive dependencies.
- `downstream`: all direct and transitive dependents.
- `paths`: all directed simple paths between two IDs.
- `--json`: machine-readable output for one-shot or shell queries.

Expected input, graph-build, and cycle errors return exit code `2`. An unknown
query ID returns an empty result.

## Input format

`INPUT` must be a JSON array:

```json
[
  {"id": 123, "name": "base", "expression": "0"},
  {"id": "derived-id", "name": "derived", "expression": "base + external_rate"}
]
```

Each item requires `id`, `name`, and `expression`. Extra fields are ignored.
IDs may be strings or integers and are normalized to strings. IDs and names
must be unique.

## Architecture

```text
JSON -> Node validation -> ANTLR expression parsing -> LineageGraph
                                                    -> DependencyCache
                                                    -> PathFinder
                         LineageService owns one consistent snapshot
```

- `ExpressionParser` returns `ParseSuccess` or recoverable `ParseFailure` and
  collects identifiers with an iterative ANTLR visitor.
- `LineageGraph` resolves names once and stores both `uses` and `used_by`
  adjacency in immutable structures.
- `DependencyCache` detects cycles and eagerly builds upstream/downstream
  closures using compact integer bitsets.
- `PathFinder` uses iterative DFS/backtracking; the cache prunes branches that
  cannot reach the target.
- `LineageService` reuses one graph/cache/path-finder snapshot and publishes a
  fully validated replacement on `reload`.

## Scope decisions

| Area | Decision |
|---|---|
| Edge direction | Calculated node -> dependency, following the brief's `revenue -> price` example. |
| Query naming | Python `snake_case`: `get_upstream`, `get_downstream`, and `find_paths`. |
| IDs | Accept JSON strings and integers; normalize both to strings. Booleans and floats are rejected. |
| Unknown expression names | Treat as external constants: record them for diagnostics but create no node or edge. |
| Invalid expressions | Parse returns a failure; graph construction aggregates failures and publishes no partial graph. |
| Duplicate identity | Reject duplicate normalized IDs and duplicate names. |
| Cycles | Reject the complete model while constructing `DependencyCache`, including self-cycles. |
| Updates | Use immutable snapshots and explicit full reload rather than mutating graph/cache state in place. |
| Missing query ID | Return an empty set/list as required. |
| Same path endpoint | Return the zero-edge path containing that valid node. |

Intentionally out of scope: automatic file watching, incremental transitive
closure updates, persistent storage, REST APIs, and path count/depth limits.
Those are production extensions rather than assignment requirements.

## Direction example

```text
report -> margin -> revenue -> price
   |        |          `-----> qty
   |        `----------------> cost
   `-------------------------> threshold
```

- Upstream follows outgoing `uses` edges.
- Downstream follows incoming `used_by` edges.
- `report-id -> price-id` is valid; the reverse path is not.
- The queried node is excluded from upstream/downstream results.

## Complexity

Let `V` be nodes, `E` resolved edges, `T` expression tokens, `W` Number 
of bits processed in one bitset word/operation, `k` Number of nodes returned 
by one closure query, and `S` total node occurrences across all returned paths.

| Operation | Time | Space |
|---|---:|---:|
| Parse + graph build | O(T + V + E) | O(V + E) |
| Cycle detection | O(V + E) | O(V) |
| Both closure caches | Worst O(E*V/W) | Worst O(V^2/W) |
| Cached closure lookup | O(1), then O(k) to iterate | O(1) extra |
| All paths | Output-sensitive, potentially exponential | O(V + S) |

The eager cache intentionally trades build memory for predictable repeated
queries, as required. Returning every simple path is inherently exponential on
some DAGs.

## Benchmark

Required 10,000-node command:

```bash
bash benchmarks/benchmark.sh --nodes 10000 --warmups 2 --runs 20
```

Measured on 2026-07-01 with CPython 3.13.12, macOS 26.5.1 arm64, and 11 logical
CPUs. Topology: a 10,000-node directed chain with 9,999 edges and one returned
path containing all 10,000 nodes.

| Section | Median | p95 |
|---|---:|---:|
| Graph build: ANTLR parsing + adjacency | 304.05 ms | 306.06 ms |
| Cache build: cycle check + both closures | 21.19 ms | 21.77 ms |
| Path finding on the prebuilt graph/cache | 11.55 ms | 11.72 ms |

The harness validates graph/edge counts, both endpoint closures, path count,
and path length during every measured run.

## Tests

```bash
.venv/bin/python -m pytest
```

The 42 tests cover parsing and recovery, graph construction, external names,
duplicates, both transitive closures, cycles, deep graphs, path enumeration,
JSON validation, CLI output, service reuse, and successful/failed reloads.

## Project layout

```text
submission/
|-- grammar/                  # Lineage.g4 and parser-generation script
|-- src/lineage/
|   |-- generated/            # committed ANTLR 4.13.2 Python output
|   |-- expression_parser.py
|   |-- graph.py
|   |-- dependency_cache.py
|   |-- path_finder.py
|   |-- service.py
|   `-- cli.py
|-- tests/
|-- benchmarks/
|-- examples/nodes.json
|-- pyproject.toml
|-- requirements.txt
|-- requirements-dev.txt
|-- setup.sh
`-- run.sh
```

To regenerate the parser after changing the grammar:

```bash
bash grammar/generate_parser.sh
```
