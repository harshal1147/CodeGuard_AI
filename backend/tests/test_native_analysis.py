import pytest

from app.services.native_analysis import analyze_native


@pytest.mark.parametrize(
    ("language", "code", "expected_issue"),
    [
        (
            "java",
            "class Runner { void run(String input) { Runtime.getRuntime().exec(input); } }",
            "command_injection_risk",
        ),
        (
            "c",
            "int main() { char buffer[8]; gets(buffer); return 0; }",
            "unsafe_buffer_function",
        ),
        (
            "cpp",
            'int main() { const char* api_token = "hidden-token"; system(api_token); return 0; }',
            "command_injection_risk",
        ),
    ],
)
def test_native_analyzers_report_language_specific_findings(language, code, expected_issue):
    report = analyze_native(code, language)

    assert expected_issue in {issue["type"] for issue in report["issues"]}
    assert report["metrics"]["quality_scores"]["overall"] < 100


def test_cpp_secret_value_is_not_included_in_report():
    report = analyze_native('const char* api_token = "hidden-token";', "cpp")

    assert "hardcoded_secret" in {issue["type"] for issue in report["issues"]}
    assert "hidden-token" not in str(report["issues"])


@pytest.mark.parametrize("language,code", [("java", "class {"), ("c", "int main( {"), ("cpp", "int main( {")])
def test_native_analyzers_report_syntax_errors(language, code):
    report = analyze_native(code, language)

    assert report["issues"][0]["type"] == "syntax_error"
