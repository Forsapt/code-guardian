from code_guardian.models import ComponentGraph, GraphNode, ScanResult, Severity

_SEVERITY_ORDER = [
    Severity.unknown,
    Severity.low,
    Severity.medium,
    Severity.high,
    Severity.critical,
]


def _max_severity(a: Severity | None, b: Severity) -> Severity:
    if a is None:
        return b
    return a if _SEVERITY_ORDER.index(a) >= _SEVERITY_ORDER.index(b) else b


def build_graph(scan_result: ScanResult) -> ComponentGraph:
    nodes: dict[str, GraphNode] = {}
    edges: set[tuple[str, str]] = set()

    for vuln in scan_result.vulnerabilities:
        target_label = vuln.target or "unknown"
        target_id = f"target:{target_label}"
        if target_id not in nodes:
            nodes[target_id] = GraphNode(
                id=target_id,
                label=target_label,
                kind="target",
                max_severity=None,
            )

        pkg_id = f"pkg:{vuln.pkg_name}@{vuln.installed_version}"
        if pkg_id not in nodes:
            nodes[pkg_id] = GraphNode(
                id=pkg_id,
                label=f"{vuln.pkg_name}@{vuln.installed_version}",
                kind="package",
                max_severity=vuln.severity,
            )
        else:
            existing = nodes[pkg_id]
            nodes[pkg_id] = GraphNode(
                id=existing.id,
                label=existing.label,
                kind="package",
                max_severity=_max_severity(existing.max_severity, vuln.severity),
            )

        edges.add((target_id, pkg_id))

        vuln_id = f"vuln:{vuln.id}"
        if vuln_id not in nodes:
            nodes[vuln_id] = GraphNode(
                id=vuln_id,
                label=vuln.id,
                kind="vulnerability",
                max_severity=vuln.severity,
            )
        edges.add((pkg_id, vuln_id))

    return ComponentGraph(nodes=nodes, edges=edges)
