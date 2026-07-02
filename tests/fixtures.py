from lineage import LineageGraph, Node


def sample_nodes() -> list[Node]:
    return [
        Node("price-id", "price", "0"),
        Node("qty-id", "qty", "0"),
        Node("cost-id", "cost", "0"),
        Node("threshold-id", "threshold", "0"),
        Node("revenue-id", "revenue", "price * qty"),
        Node("margin-id", "margin", "revenue - cost"),
        Node(
            "report-id",
            "report",
            "if (margin > threshold) then margin else 0",
        ),
    ]


def sample_graph() -> LineageGraph:
    return LineageGraph(sample_nodes())


def diamond_graph() -> LineageGraph:
    return LineageGraph(
        [
            Node("d", "d", "0"),
            Node("b", "b", "d"),
            Node("c", "c", "d"),
            Node("a", "a", "b + c"),
        ]
    )
