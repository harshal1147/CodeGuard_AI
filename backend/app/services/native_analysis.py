from functools import lru_cache
import re
from typing import Any

try:
    from tree_sitter import Node
    from tree_sitter_language_pack import get_parser
except ImportError:
    Node = Any
    get_parser = None

from app.services.analysis_service import _complexity_rating, _score

LOOP_NODES = {"for_statement", "enhanced_for_statement", "while_statement", "do_statement"}
BRANCH_NODES = {"if_statement", "switch_statement", "catch_clause", "case_statement", "case_label"}
SECRET_PATTERN = re.compile(
    r"(?i)\b[A-Za-z_$][\w$]*(?:password|passwd|secret|token|api[_]?key)[\w$]*\s*=\s*(['\"])[^'\"\r\n]*\1"
)
UNSAFE_C_FUNCTIONS = {"gets", "strcpy", "strcat", "sprintf", "vsprintf"}


@lru_cache(maxsize=3)
def _parser(language: str):
    return get_parser(language)


def _walk(root: Node):
    stack = [root]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(reversed(node.children))


def _text(source: bytes, node: Node | None) -> str:
    if node is None:
        return ""
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _add_issue(
    issues: list[dict],
    *,
    issue_type: str,
    severity: str,
    title: str,
    message: str,
    line: int,
    recommendation: str,
    category: str,
    confidence: str = "MEDIUM",
) -> None:
    issues.append(
        {
            "type": issue_type,
            "severity": severity,
            "title": title,
            "message": message,
            "line": line,
            "recommendation": recommendation,
            "category": category,
            "confidence": confidence,
        }
    )


def _complexity(root: Node, source: bytes) -> dict:
    branch_count = 0
    loop_depth_max = 0
    has_sort = False
    has_dynamic_collection = False

    def visit(node: Node, loop_depth: int) -> None:
        nonlocal branch_count, loop_depth_max, has_sort, has_dynamic_collection
        if node.type in BRANCH_NODES:
            branch_count += 1
        if node.type in LOOP_NODES:
            branch_count += 1
            loop_depth += 1
            loop_depth_max = max(loop_depth_max, loop_depth)
        if node.type in {
            "array_declarator",
            "array_creation_expression",
            "new_array_expression",
            "object_creation_expression",
            "new_expression",
            "initializer_list",
        }:
            has_dynamic_collection = True
        if node.type in {"call_expression", "method_invocation"}:
            call = _text(source, node.child_by_field_name("function") or node.child_by_field_name("name"))
            if not call:
                call = _text(source, node)
            if re.search(r"(?:^|::|\.)sort(?:\s*\(|$)", call):
                has_sort = True
        for child in node.children:
            visit(child, loop_depth)

    visit(root, 0)
    if loop_depth_max >= 3:
        time_complexity = "O(n^3+)"
    elif loop_depth_max == 2:
        time_complexity = "O(n^2)"
    elif loop_depth_max == 1:
        time_complexity = "O(n)"
    elif has_sort:
        time_complexity = "O(n log n)"
    else:
        time_complexity = "O(1)"

    cyclomatic = branch_count + 1
    return {
        "cyclomatic_complexity": cyclomatic,
        "cyclomatic_rating": _complexity_rating(cyclomatic),
        "estimated_time_complexity": time_complexity,
        "estimated_space_complexity": "O(n)" if has_dynamic_collection else "O(1)",
        "complexity_is_estimate": True,
    }


def _syntax_error(language: str, line: int) -> dict:
    return {
        "type": "syntax_error",
        "severity": "HIGH",
        "title": f"{language.upper()} syntax error",
        "message": "The parser found invalid or incomplete syntax near this line.",
        "line": line,
        "recommendation": "Correct the syntax at the reported line and run the analysis again.",
        "category": "correctness",
        "confidence": "HIGH",
    }


def _syntax_failure_report(language: str, line: int) -> dict:
    issue = _syntax_error(language, line)
    metrics = {
        "cyclomatic_complexity": None,
        "cyclomatic_rating": "Unavailable",
        "estimated_time_complexity": "Unavailable",
        "estimated_space_complexity": "Unavailable",
        "complexity_is_estimate": True,
        "quality_scores": _score([issue], {"cyclomatic_complexity": 1, "estimated_time_complexity": "O(1)"}),
    }
    return {"issues": [issue], "metrics": metrics}


def _fallback(language: str, code: str) -> dict:
    issues: list[dict] = []
    patterns = [
        ("hardcoded_secret", "HIGH", "Possible hardcoded secret", SECRET_PATTERN, "A credential-like variable is assigned a string literal. The value is intentionally not included in this report.", "Load secrets from a secret manager or environment variable and rotate any exposed credential.", "security"),
    ]
    if language == "java":
        patterns.extend([
            ("command_injection_risk", "HIGH", "Shell command execution", re.compile(r"Runtime\s*\.\s*getRuntime\s*\(\s*\)\s*\.\s*exec\s*\("), "Runtime.exec() can invoke commands using untrusted input.", "Avoid shell command construction and validate every argument passed to a process.", "security"),
            ("unsafe_deserialization", "HIGH", "Unsafe Java deserialization", re.compile(r"\breadObject\s*\("), "Deserializing untrusted Java objects can lead to remote code execution.", "Do not deserialize untrusted data; use a safe data format and strict allow-lists.", "security"),
        ])
    else:
        patterns.extend([
            ("unsafe_buffer_function", "HIGH", "Unsafe buffer function", re.compile(r"\b(?:gets|strcpy|strcat|sprintf|vsprintf)\s*\("), "This C/C++ function does not safely constrain the destination buffer.", "Use bounded alternatives and validate buffer lengths before copying or formatting.", "security"),
            ("command_injection_risk", "HIGH", "Shell command execution", re.compile(r"\b(?:system|popen)\s*\("), "Shell command execution is risky when command strings contain untrusted input.", "Avoid passing untrusted text to a shell; use structured process APIs and validate arguments.", "security"),
        ])
    for issue_type, severity, title, pattern, message, recommendation, category in patterns:
        for match in pattern.finditer(code):
            _add_issue(
                issues,
                issue_type=issue_type,
                severity=severity,
                title=title,
                message=message,
                line=code.count("\n", 0, match.start()) + 1,
                recommendation=recommendation,
                category=category,
                confidence="LOW",
            )

    loop_count = len(re.findall(r"\b(?:for|while)\s*\(", code))
    if loop_count >= 3:
        time_complexity = "O(n^3+)"
    elif loop_count == 2:
        time_complexity = "O(n^2)"
    elif loop_count == 1:
        time_complexity = "O(n)"
    else:
        time_complexity = "O(n log n)" if re.search(r"(?:sort|qsort)\s*\(", code) else "O(1)"
    branch_count = len(re.findall(r"\b(?:if|for|while|case|catch)\b|&&|\|\|", code))
    metrics = {
        "cyclomatic_complexity": branch_count + 1,
        "cyclomatic_rating": _complexity_rating(branch_count + 1),
        "estimated_time_complexity": time_complexity,
        "estimated_space_complexity": "O(n)" if re.search(r"\[[^\]]*\]", code) else "O(1)",
        "complexity_is_estimate": True,
        "parser_mode": "heuristic-fallback",
        "quality_scores": _score(issues, {"cyclomatic_complexity": branch_count + 1, "estimated_time_complexity": time_complexity}),
    }
    return {"issues": issues, "metrics": metrics}


def analyze_native(code: str, language: str) -> dict:
    if language not in {"java", "c", "cpp"}:
        raise ValueError(f"Unsupported native language: {language}")
    if get_parser is None:
        return _fallback(language, code)

    source = code.encode("utf-8")
    root = _parser(language).parse(source).root_node
    syntax_error = next((node for node in _walk(root) if node.type == "ERROR" or node.is_missing), None)
    if syntax_error is not None:
        return _syntax_failure_report(language, syntax_error.start_point.row + 1)

    issues: list[dict] = []
    for match in SECRET_PATTERN.finditer(code):
        _add_issue(
            issues,
            issue_type="hardcoded_secret",
            severity="HIGH",
            title="Possible hardcoded secret",
            message="A credential-like variable is assigned a string literal. The value is intentionally not included in this report.",
            line=code.count("\n", 0, match.start()) + 1,
            recommendation="Load secrets from a secret manager or environment variable and rotate any exposed credential.",
            category="security",
        )

    for node in _walk(root):
        if node.type not in {"call_expression", "method_invocation"}:
            continue
        line = node.start_point.row + 1
        function_node = node.child_by_field_name("function") or node.child_by_field_name("name")
        call = re.sub(r"\s+", "", _text(source, function_node))
        full_call = re.sub(r"\s+", "", _text(source, node))
        call_tail = call.split("::")[-1].split(".")[-1]

        if language in {"c", "cpp"} and call_tail in UNSAFE_C_FUNCTIONS:
            _add_issue(
                issues,
                issue_type="unsafe_buffer_function",
                severity="HIGH",
                title="Unsafe buffer function",
                message=f"{call_tail}() does not safely constrain the destination buffer and may overflow it.",
                line=line,
                recommendation="Use bounded alternatives and validate buffer lengths before copying or formatting.",
                category="security",
                confidence="HIGH",
            )
        if language in {"c", "cpp"} and call_tail in {"system", "popen"}:
            _add_issue(
                issues,
                issue_type="command_injection_risk",
                severity="HIGH",
                title="Shell command execution",
                message=f"{call_tail}() invokes a shell and is unsafe when command text contains untrusted input.",
                line=line,
                recommendation="Avoid passing untrusted text to a shell; use structured process APIs and validate arguments.",
                category="security",
                confidence="MEDIUM",
            )
        if language == "java" and call_tail == "exec" and "Runtime.getRuntime()" in full_call:
            _add_issue(
                issues,
                issue_type="command_injection_risk",
                severity="HIGH",
                title="Runtime command execution",
                message="Runtime.exec() can run commands built from untrusted input.",
                line=line,
                recommendation="Avoid shell command construction and validate every argument passed to a process.",
                category="security",
                confidence="MEDIUM",
            )
        if language == "java" and call_tail == "readObject":
            _add_issue(
                issues,
                issue_type="unsafe_deserialization",
                severity="HIGH",
                title="Unsafe Java deserialization",
                message="Deserializing untrusted Java objects can lead to remote code execution.",
                line=line,
                recommendation="Do not deserialize untrusted data; use a safe data format and strict allow-lists.",
                category="security",
                confidence="MEDIUM",
            )
        if call_tail in {"query", "execute"} and re.search(r"(?:\+|\$\{).*", full_call):
            _add_issue(
                issues,
                issue_type="sql_injection_risk",
                severity="HIGH",
                title="Potential SQL injection",
                message="A query-like call appears to build its statement using concatenated or interpolated input.",
                line=line,
                recommendation="Use parameterized queries and pass values separately from the SQL statement.",
                category="security",
                confidence="LOW",
            )

    unique_issues: list[dict] = []
    seen: set[tuple[str, int | None]] = set()
    for issue in issues:
        signature = (issue["type"], issue["line"])
        if signature not in seen:
            seen.add(signature)
            unique_issues.append(issue)

    metrics = _complexity(root, source)
    metrics["quality_scores"] = _score(unique_issues, metrics)
    return {"issues": unique_issues, "metrics": metrics}
