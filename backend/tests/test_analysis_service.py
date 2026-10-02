from app.services.analysis_service import analyze_python


def test_python_analyzer_reports_findings_without_exposing_secret():
    report = analyze_python(
        "api_token = 'do-not-return-this'\n"
        "def compute(values=[]):\n"
        "    return eval(values[0]) / 0\n"
    )

    issue_types = {issue["type"] for issue in report["issues"]}
    assert {"hardcoded_secret", "mutable_default_argument", "dynamic_code_execution", "division_by_zero"} <= issue_types
    assert all("do-not-return-this" not in str(issue) for issue in report["issues"])
    assert 0 <= report["metrics"]["quality_scores"]["overall"] <= 100


def test_python_analyzer_estimates_nested_loop_complexity():
    report = analyze_python("for left in values:\n    for right in values:\n        print(left, right)\n")

    assert report["metrics"]["estimated_time_complexity"] == "O(n^2)"
    assert report["metrics"]["complexity_is_estimate"] is True


def test_python_analyzer_reports_syntax_error():
    report = analyze_python("def broken(:\n    pass\n")

    assert report["issues"][0]["type"] == "syntax_error"
    assert report["issues"][0]["line"] == 1

def test_quality_scores_reflect_detected_risks_and_complexity():
    clean = analyze_python("value = 1")
    security_issue = analyze_python("result = eval(source)")
    syntax_issue = analyze_python("def broken(:")
    nested_loops = analyze_python("for left in values:\n    for right in values:\n        pass")
    complex_branches = analyze_python("\n".join(f"if flag_{index}:\n    pass" for index in range(6)))
    long_function = analyze_python("def process():\n" + "    value = 1\n" * 41)

    assert all(score == 100 for score in clean["metrics"]["quality_scores"].values())
    assert security_issue["metrics"]["quality_scores"]["security"] < 100
    assert syntax_issue["metrics"]["quality_scores"]["correctness"] < 100
    assert nested_loops["metrics"]["quality_scores"]["performance"] < 100
    assert complex_branches["metrics"]["quality_scores"]["readability"] < 100
    assert long_function["metrics"]["quality_scores"]["maintainability"] < 100
