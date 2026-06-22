from code_guardian.graph.builder import build_graph
from code_guardian.models import ScanResult, Severity, Vulnerability


def _vuln(pkg: str, version: str, severity: Severity, target: str = "package-lock.json") -> Vulnerability:
    return Vulnerability(
        id=f"CVE-{pkg}",
        pkg_name=pkg,
        installed_version=version,
        fixed_version="",
        severity=severity,
        title=pkg,
        target=target,
    )


def test_build_graph_creates_target_and_package_nodes():
    result = ScanResult(vulnerabilities=[_vuln("lodash", "4.17.20", Severity.high)])
    graph = build_graph(result)
    assert "target:package-lock.json" in graph.nodes
    assert "pkg:lodash@4.17.20" in graph.nodes


def test_build_graph_creates_edge():
    result = ScanResult(vulnerabilities=[_vuln("lodash", "4.17.20", Severity.high)])
    graph = build_graph(result)
    assert ("target:package-lock.json", "pkg:lodash@4.17.20") in graph.edges


def test_build_graph_deduplicates_packages():
    result = ScanResult(
        vulnerabilities=[
            _vuln("lodash", "4.17.20", Severity.medium, "package-lock.json"),
            _vuln("lodash", "4.17.20", Severity.critical, "yarn.lock"),
        ]
    )
    graph = build_graph(result)
    pkg_nodes = [n for n in graph.nodes.values() if n.kind == "package"]
    assert len(pkg_nodes) == 1
    assert pkg_nodes[0].max_severity == Severity.critical


def test_build_graph_max_severity_wins():
    result = ScanResult(
        vulnerabilities=[
            _vuln("express", "4.17.1", Severity.low),
            _vuln("express", "4.17.1", Severity.high),
            _vuln("express", "4.17.1", Severity.medium),
        ]
    )
    graph = build_graph(result)
    node = graph.nodes["pkg:express@4.17.1"]
    assert node.max_severity == Severity.high


def test_to_dot_returns_valid_dot_string():
    result = ScanResult(
        vulnerabilities=[_vuln("lodash", "4.17.20", Severity.critical)]
    )
    graph = build_graph(result)
    dot = graph.to_dot()
    assert "digraph" in dot
    assert "lodash@4.17.20" in dot
    assert "#dd3333" in dot


def test_build_graph_empty_scan_result():
    graph = build_graph(ScanResult())
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0
