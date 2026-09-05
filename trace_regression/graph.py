from __future__ import annotations

from dataclasses import dataclass, field

from trace_regression.normalize import service_name


@dataclass
class SpanNode:
    trace_id: str
    span_id: str
    parent_span_id: str | None
    service: str
    name: str
    start_ns: int
    end_ns: int
    status: str
    attributes: dict
    children: list[str] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        return max(0, self.end_ns - self.start_ns) / 1_000_000.0


@dataclass
class TraceGraph:
    trace_id: str
    nodes: dict[str, SpanNode]
    roots: list[str]


def build_trace_graph(spans: list[dict]) -> TraceGraph:
    if not spans:
        return TraceGraph(
            trace_id="",
            nodes={},
            roots=[],
        )

    nodes: dict[str, SpanNode] = {}

    for span in spans:
        node = SpanNode(
            trace_id=span["trace_id"],
            span_id=span["span_id"],
            parent_span_id=span.get("parent_span_id"),
            service=service_name(span),
            name=span["name"],
            start_ns=int(span.get("start_time_unix_nano") or 0),
            end_ns=int(span.get("end_time_unix_nano") or 0),
            status=span.get("status", "UNSET"),
            attributes=dict(span.get("attributes") or {}),
        )

        nodes[node.span_id] = node

    roots = []

    for node in nodes.values():
        if (
            node.parent_span_id
            and node.parent_span_id in nodes
        ):
            nodes[node.parent_span_id].children.append(
                node.span_id
            )
        else:
            roots.append(node.span_id)

    for node in nodes.values():
        node.children.sort(
            key=lambda child_id: (
                nodes[child_id].start_ns,
                nodes[child_id].end_ns,
            )
        )

    roots.sort(
        key=lambda root_id: (
            nodes[root_id].start_ns,
            nodes[root_id].end_ns,
        )
    )

    return TraceGraph(
        trace_id=spans[0]["trace_id"],
        nodes=nodes,
        roots=roots,
    )


def semantic_key(
    node: SpanNode,
    graph: TraceGraph,
) -> tuple[str, str, str]:
    parent = None

    if node.parent_span_id:
        parent = graph.nodes.get(node.parent_span_id)

    parent_name = (
        parent.name
        if parent is not None
        else "ROOT"
    )

    return (
        node.service,
        node.name,
        parent_name,
    )


def graph_edges(
    graph: TraceGraph,
) -> list[dict]:
    edges = []

    for node in graph.nodes.values():
        for child_id in node.children:
            child = graph.nodes[child_id]

            edges.append(
                {
                    "parent_service": node.service,
                    "parent_span": node.name,
                    "child_service": child.service,
                    "child_span": child.name,
                }
            )

    return edges
