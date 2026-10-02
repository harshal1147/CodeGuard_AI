from app.services.javascript_analysis import analyze_javascript
from app.services import javascript_analysis


def test_javascript_reports_security_and_bug_findings():
    code = """
const api_token = 'do-not-return-this';
function run(values = []) {
  if (values) {
    eval(values[0]);
  }
  for (const item of values) {
    for (const other of values) {}
  }
  document.body.innerHTML = values[0];
  return 1 / 0;
}
"""
    report = analyze_javascript(code)

    issue_types = {issue["type"] for issue in report["issues"]}
    assert {
        "hardcoded_secret",
        "dynamic_code_execution",
        "unsafe_html_injection",
        "division_by_zero",
    } <= issue_types
    assert "do-not-return-this" not in str(report["issues"])
    assert report["metrics"]["estimated_time_complexity"] == "O(n^2)"
    assert report["metrics"]["complexity_is_estimate"] is True
    assert report["metrics"]["quality_scores"]["security"] < 100
    assert report["metrics"]["quality_scores"]["performance"] < 100


def test_typescript_parses_types_and_detects_eval():
    report = analyze_javascript("const input: string = source; const output = eval(input);", "typescript")

    assert "dynamic_code_execution" in {issue["type"] for issue in report["issues"]}
    assert not any(issue["type"] == "syntax_error" for issue in report["issues"])


def test_javascript_reports_syntax_errors():
    report = analyze_javascript("function broken( {\n")

    assert report["issues"][0]["type"] == "syntax_error"
    assert report["issues"][0]["line"] == 1


def test_javascript_uses_labeled_fallback_when_parser_is_unavailable(monkeypatch):
    monkeypatch.setattr(javascript_analysis, "get_parser", None)
    report = javascript_analysis.analyze_javascript(
        "const access_token = 'never-return-this'; eval(source);\n"
        "for (const item of items) { for (const other of items) {} }"
    )

    assert report["metrics"]["parser_mode"] == "heuristic-fallback"
    assert report["metrics"]["estimated_time_complexity"] == "O(n^2)"
    assert {issue["type"] for issue in report["issues"]} >= {"hardcoded_secret", "dynamic_code_execution"}
    assert all(issue["confidence"] == "LOW" for issue in report["issues"])
    assert "never-return-this" not in str(report["issues"])
