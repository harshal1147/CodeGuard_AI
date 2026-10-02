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

SECRET_PARTS = ("password", "passwd", "secret", "token", "api_key", "apikey")
LOOP_NODES = {"for_statement", "for_in_statement", "while_statement", "do_statement"}
BRANCH_NODES = {"if_statement", "conditional_expression", "switch_case", *LOOP_NODES}


@lru_cache(maxsize=2)
def _parser(language: str):
    return get_parser(language)


def _fallback_analysis(code: str, language: str) -> dict:
    issues: list[dict] = []
    patterns = [
        (
            "hardcoded_secret",
            "HIGH",
            "Possible hardcoded secret",
            r"(?i)\b[A-Za-z_$][\w$]*(?:password|passwd|secret|token|api_key|apikey)[\w$]*\s*[:=]\s*(['\"])[^'\"\r\n]*\1",
            "A credential-like variable is assigned a string literal. The value is intentionally not included in this report.",
            "Load secrets from a secret manager or environment variable and rotate any exposed credential.",
            "security",
        ),
        (
            "dynamic_code_execution",
            "HIGH",
            "Dynamic code execution",
            r"\beval\s*\(",
            "eval() executes dynamically supplied JavaScript and can lead to code injection.",
            "Avoid eval(); parse data as JSON or map input to explicitly allowed operations.",
            "security",
        ),
        (
            "command_injection_risk",
            "HIGH",
            "Shell command execution",
            r"\b(?:exec|execSync)\s*\(",
            "This call invokes a shell and may be unsafe when command text includes untrusted input.",
            "Prefer argument-array process APIs with shell disabled and validate user-controlled arguments.",
            "security",
        ),
        (
            "unsafe_html_injection",
            "MEDIUM",
            "Potential unsafe HTML injection",
            r"\binnerHTML\s*=(?!=)",
            "The code writes a value directly to innerHTML, which can enable cross-site scripting if the value is untrusted.",
            "Prefer textContent or sanitize input with a trusted HTML sanitizer before inserting markup.",
            "security",
        ),
        (
            "sql_injection_risk",
            "HIGH",
            "Potential SQL injection",
            r"\b(?:query|execute)\s*\(\s*`",
            "A template string is passed directly to a query-like method.",
            "Use parameterized queries and pass values separately from the SQL statement.",
            "security",
        ),
        (
            "division_by_zero",
            "HIGH",
            "Division by zero",
            r"/\s*0(?:\.0)?\b",
            "This expression divides by a literal zero and will produce a non-finite result.",
            "Validate the denominator before performing the division.",
            "bug",
        ),
    ]
    for issue_type, severity, title, pattern, message, recommendation, category in patterns:
        for match in re.finditer(pattern, code):
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

    loops = len(re.findall(r"\b(?:for|while)\s*\(", code))
    branches = len(re.findall(r"\b(?:if|for|while|case)\s*\(|&&|\|\|", code))
    if loops > 1:
        time_complexity = "O(n^2)"
    elif loops == 1:
        time_complexity = "O(n)"
    elif re.search(r"\.sort\s*\(", code):
        time_complexity = "O(n log n)"
    else:
        time_complexity = "O(1)"
    metrics = {
        "cyclomatic_complexity": branches + 1,
        "cyclomatic_rating": _complexity_rating(branches + 1),
        "estimated_time_complexity": time_complexity,
        "estimated_space_complexity": "O(n)" if re.search(r"\[\s*(?:\]|[^\]])", code) else "O(1)",
        "complexity_is_estimate": True,
        "parser_mode": "heuristic-fallback",
    }
    metrics["quality_scores"] = _score(issues, metrics)
    return {"issues": issues, "metrics": metrics}


def _walk(root: Node):
    stack = [root]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(reversed(node.children))


def _source(source: bytes, node: Node | None) -> str:
    if node is None:
        return ""
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _call_name(source: bytes, node: Node | None) -> str:
    return _source(source, node).replace(" ", "")


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


def _first_syntax_error(root: Node) -> Node | None:
    for node in _walk(root):
        if node.type == "ERROR" or node.is_missing:
            return node
    return None


def _estimate_complexity(root: Node, source: bytes) -> dict:
    branch_count = 0
    max_loop_depth = 0
    has_sort = False
    grows_collection = False

    def visit(node: Node, loop_depth: int) -> None:
        nonlocal branch_count, max_loop_depth, has_sort, grows_collection
        if node.type in BRANCH_NODES:
            branch_count += 1
        if node.type in LOOP_NODES:
            loop_depth += 1
            max_loop_depth = max(max_loop_depth, loop_depth)
        if node.type in {"array", "object", "array_pattern", "object_pattern"}:
            grows_collection = True
        if node.type == "call_expression":
            call_name = _call_name(source, node.child_by_field_name("function"))
            if call_name == "sort" or call_name.endswith(".sort"):
                has_sort = True
        if node.type == "binary_expression":
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")
            if left is not None and right is not None:
                operator = source[left.end_byte:right.start_byte].decode("utf-8", errors="replace").strip()
                if operator in {"&&", "||", "??"}:
                    branch_count += 1
        for child in node.children:
            visit(child, loop_depth)

    visit(root, 0)
    if max_loop_depth >= 3:
        time_complexity = "O(n^3+)"
    elif max_loop_depth == 2:
        time_complexity = "O(n^2)"
    elif max_loop_depth == 1:
        time_complexity = "O(n)"
    elif has_sort:
        time_complexity = "O(n log n)"
    else:
        time_complexity = "O(1)"

    cyclomatic = 1 + branch_count
    return {
        "cyclomatic_complexity": cyclomatic,
        "cyclomatic_rating": _complexity_rating(cyclomatic),
        "estimated_time_complexity": time_complexity,
        "estimated_space_complexity": "O(n)" if grows_collection else "O(1)",
        "complexity_is_estimate": True,
    }


def analyze_javascript(code: str, language: str = "javascript") -> dict:
    parser_language = "typescript" if language in {"typescript", "tsx"} else "javascript"
    if get_parser is None:
        return _fallback_analysis(code, parser_language)
    source = code.encode("utf-8")
    tree = _parser(parser_language).parse(source)
    root = tree.root_node
    syntax_error = _first_syntax_error(root)

    if syntax_error is not None:
        line = syntax_error.start_point.row + 1
        issue = {
            "type": "syntax_error",
            "severity": "HIGH",
            "title": f"{parser_language.title()} syntax error",
            "message": "The parser found invalid or incomplete syntax near this line.",
            "line": line,
            "recommendation": "Correct the syntax at the reported line and run the analysis again.",
            "category": "correctness",
            "confidence": "HIGH",
        }
        metrics = {
            "cyclomatic_complexity": None,
            "cyclomatic_rating": "Unavailable",
            "estimated_time_complexity": "Unavailable",
            "estimated_space_complexity": "Unavailable",
            "complexity_is_estimate": True,
            "quality_scores": _score([issue], {"cyclomatic_complexity": 1, "estimated_time_complexity": "O(1)"}),
        }
        return {"issues": [issue], "metrics": metrics}

    issues: list[dict] = []
    for node in _walk(root):
        line = node.start_point.row + 1
        if node.type in {"variable_declarator", "assignment_expression"}:
            name_node = node.child_by_field_name("name") or node.child_by_field_name("left")
            value_node = node.child_by_field_name("value") or node.child_by_field_name("right")
            name = _source(source, name_node).lower()
            if any(part in name for part in SECRET_PARTS) and value_node is not None and value_node.type in {"string", "template_string"}:
                _add_issue(
                    issues,
                    issue_type="hardcoded_secret",
                    severity="HIGH",
                    title="Possible hardcoded secret",
                    message="A credential-like variable is assigned a string literal. The value is intentionally not included in this report.",
                    line=line,
                    recommendation="Load secrets from a secret manager or environment variable and rotate any exposed credential.",
                    category="security",
                    confidence="MEDIUM",
                )

        if node.type == "call_expression":
            function = node.child_by_field_name("function")
            call_name = _call_name(source, function)
            if call_name == "eval" or call_name.endswith(".eval"):
                _add_issue(
                    issues,
                    issue_type="dynamic_code_execution",
                    severity="HIGH",
                    title="Dynamic code execution",
                    message="eval() executes dynamically supplied JavaScript and can lead to code injection.",
                    line=line,
                    recommendation="Avoid eval(); parse data as JSON or map input to explicitly allowed operations.",
                    category="security",
                    confidence="HIGH",
                )
            if call_name in {"exec", "execSync", "child_process.exec", "child_process.execSync"}:
                _add_issue(
                    issues,
                    issue_type="command_injection_risk",
                    severity="HIGH",
                    title="Shell command execution",
                    message="This call invokes a shell and may be unsafe when command text includes untrusted input.",
                    line=line,
                    recommendation="Prefer argument-array process APIs with shell disabled and validate all user-controlled arguments.",
                    category="security",
                    confidence="MEDIUM",
                )
            if call_name.endswith((".query", ".execute")):
                arguments = node.child_by_field_name("arguments")
                first_argument = arguments.named_children[0] if arguments and arguments.named_children else None
                if first_argument is not None and first_argument.type == "template_string":
                    _add_issue(
                        issues,
                        issue_type="sql_injection_risk",
                        severity="HIGH",
                        title="Potential SQL injection",
                        message="A template string is passed directly to a query-like method.",
                        line=line,
                        recommendation="Use parameterized queries and pass values separately from the SQL statement.",
                        category="security",
                        confidence="MEDIUM",
                    )

        if node.type == "assignment_expression":
            left = node.child_by_field_name("left")
            if left is not None and left.type == "member_expression" and _source(source, left.child_by_field_name("property")) == "innerHTML":
                _add_issue(
                    issues,
                    issue_type="unsafe_html_injection",
                    severity="MEDIUM",
                    title="Potential unsafe HTML injection",
                    message="The assignment writes a value directly to innerHTML, which can enable cross-site scripting if the value is untrusted.",
                    line=line,
                    recommendation="Prefer textContent or sanitize input with a trusted HTML sanitizer before inserting markup.",
                    category="security",
                    confidence="MEDIUM",
                )

        if node.type == "binary_expression":
            right = node.child_by_field_name("right")
            left = node.child_by_field_name("left")
            operator = source[left.end_byte:right.start_byte].decode("utf-8", errors="replace").strip() if left and right else ""
            if operator == "/" and _source(source, right).strip() in {"0", "0.0"}:
                _add_issue(
                    issues,
                    issue_type="division_by_zero",
                    severity="HIGH",
                    title="Division by zero",
                    message="This expression divides by a literal zero and will produce a non-finite result.",
                    line=line,
                    recommendation="Validate the denominator before performing the division.",
                    category="bug",
                    confidence="HIGH",
                )

    unique_issues: list[dict] = []
    seen: set[tuple[str, int]] = set()
    for issue in issues:
        signature = (issue["type"], issue["line"])
        if signature not in seen:
            seen.add(signature)
            unique_issues.append(issue)

    metrics = _estimate_complexity(root, source)
    metrics["quality_scores"] = _score(unique_issues, metrics)
    return {"issues": unique_issues, "metrics": metrics}
