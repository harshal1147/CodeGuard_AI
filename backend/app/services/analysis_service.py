import ast

SEVERITY_PENALTIES = {"CRITICAL": 25, "HIGH": 15, "MEDIUM": 8, "LOW": 3, "INFO": 0}
SECRET_NAMES = ("password", "passwd", "secret", "token", "api_key", "apikey")


class _AnalysisVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.issues: list[dict] = []
        self.branch_count = 0
        self.loop_depth = 0
        self.max_loop_depth = 0
        self.has_sort = False

    def add_issue(
        self,
        *,
        issue_type: str,
        severity: str,
        title: str,
        message: str,
        line: int | None,
        recommendation: str,
        category: str,
        confidence: str = "MEDIUM",
    ) -> None:
        self.issues.append(
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

    def visit_If(self, node: ast.If) -> None:
        self.branch_count += 1
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.branch_count += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.branch_count += max(0, len(node.values) - 1)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.branch_count += 1
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.add_issue(
                issue_type="empty_exception_handler",
                severity="MEDIUM",
                title="Empty exception handler",
                message="This exception handler suppresses errors without taking action.",
                line=node.lineno,
                recommendation="Handle the expected error, add useful logging, or remove the handler.",
                category="bug",
                confidence="HIGH",
            )
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self._visit_loop(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._visit_loop(node)

    def visit_While(self, node: ast.While) -> None:
        self._visit_loop(node)

    def _visit_loop(self, node: ast.For | ast.AsyncFor | ast.While) -> None:
        self.branch_count += 1
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_Match(self, node: ast.Match) -> None:
        self.branch_count += max(0, len(node.cases) - 1)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = _call_name(node.func)
        if name in {"eval", "exec"}:
            self.add_issue(
                issue_type="dynamic_code_execution",
                severity="HIGH",
                title="Dynamic code execution",
                message=f"Call to {name}() can execute dynamically supplied code.",
                line=node.lineno,
                recommendation="Avoid dynamic code execution; use an explicit parser or a constrained mapping of allowed operations.",
                category="security",
                confidence="HIGH",
            )
        if name in {"os.system", "subprocess.run", "subprocess.call", "subprocess.Popen"}:
            shell_enabled = any(
                keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True
                for keyword in node.keywords
            )
            if name == "os.system" or shell_enabled:
                self.add_issue(
                    issue_type="command_injection_risk",
                    severity="HIGH",
                    title="Shell command execution",
                    message="This call invokes a shell, which can be unsafe when arguments include untrusted input.",
                    line=node.lineno,
                    recommendation="Prefer subprocess with an argument list and shell=False; validate any user-controlled arguments.",
                    category="security",
                    confidence="MEDIUM",
                )
        if name.endswith((".execute", ".executemany")) and node.args:
            query = node.args[0]
            if isinstance(query, (ast.JoinedStr, ast.BinOp)):
                self.add_issue(
                    issue_type="sql_injection_risk",
                    severity="HIGH",
                    title="Potential SQL injection",
                    message="The SQL statement is constructed dynamically before execution.",
                    line=node.lineno,
                    recommendation="Use parameterized queries and pass values separately from the SQL statement.",
                    category="security",
                    confidence="MEDIUM",
                )
        if name in {"sorted", "list.sort"} or name.endswith(".sort"):
            self.has_sort = True
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        targets = [name for target in node.targets for name in _target_names(target)]
        self._check_secret_assignment(targets, node.value, node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        targets = list(_target_names(node.target))
        if node.value is not None:
            self._check_secret_assignment(targets, node.value, node.lineno)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_mutable_defaults(node)
        self._check_function_design(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_mutable_defaults(node)
        self._check_function_design(node)
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)) and isinstance(node.right, ast.Constant):
            if node.right.value == 0:
                self.add_issue(
                    issue_type="division_by_zero",
                    severity="HIGH",
                    title="Division by zero",
                    message="This expression divides by a literal zero and will fail at runtime.",
                    line=node.lineno,
                    recommendation="Check the divisor before performing the operation.",
                    category="bug",
                    confidence="HIGH",
                )
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        if any(isinstance(operator, (ast.Eq, ast.NotEq)) for operator in node.ops):
            if any(isinstance(value, ast.Constant) and value.value is None for value in [node.left, *node.comparators]):
                self.add_issue(
                    issue_type="none_comparison",
                    severity="LOW",
                    title="Use identity comparison for None",
                    message="The code compares a value to None with equality rather than identity.",
                    line=node.lineno,
                    recommendation="Use `is None` or `is not None` for None checks.",
                    category="maintainability",
                    confidence="HIGH",
                )
        self.generic_visit(node)

    def _check_secret_assignment(self, names: list[str], value: ast.expr, line: int) -> None:
        secret_name = any(any(part in name.lower() for part in SECRET_NAMES) for name in names)
        if secret_name and isinstance(value, ast.Constant) and isinstance(value.value, str) and value.value:
            self.add_issue(
                issue_type="hardcoded_secret",
                severity="HIGH",
                title="Possible hardcoded secret",
                message="A credential-like variable is assigned a string literal. The value is intentionally not included in this report.",
                line=line,
                recommendation="Load secrets from a secret manager or environment variable and rotate any exposed credential.",
                category="security",
                confidence="MEDIUM",
            )

    def _check_mutable_defaults(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        defaults = [*node.args.defaults, *(default for default in node.args.kw_defaults if default is not None)]
        for default in defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.add_issue(
                    issue_type="mutable_default_argument",
                    severity="MEDIUM",
                    title="Mutable function default",
                    message=f"Function `{node.name}` uses a mutable object as a default argument.",
                    line=default.lineno,
                    recommendation="Use None as the default and create a new mutable value inside the function.",
                    category="bug",
                    confidence="HIGH",
                )

    def _check_function_design(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        if node.end_lineno - node.lineno + 1 > 40:
            self.add_issue(
                issue_type="long_function",
                severity="MEDIUM",
                title="Long function",
                message=f"Function `{node.name}` spans more than 40 lines, which can make it harder to understand and maintain.",
                line=node.lineno,
                recommendation="Split the function into smaller, purpose-focused helpers.",
                category="maintainability",
                confidence="HIGH",
            )

        parameter_count = len(node.args.posonlyargs) + len(node.args.args) + len(node.args.kwonlyargs)
        if parameter_count > 5:
            self.add_issue(
                issue_type="too_many_parameters",
                severity="LOW",
                title="Function has many parameters",
                message=f"Function `{node.name}` has more than five parameters.",
                line=node.lineno,
                recommendation="Group related inputs into a data structure or split responsibilities.",
                category="maintainability",
                confidence="HIGH",
            )


def _call_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _target_names(node: ast.expr) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, (ast.Tuple, ast.List)):
        return [name for element in node.elts for name in _target_names(element)]
    return []


def _estimate_complexity(visitor: _AnalysisVisitor, tree: ast.AST) -> dict:
    if visitor.max_loop_depth >= 3:
        time_complexity = "O(n^3+)"
    elif visitor.max_loop_depth == 2:
        time_complexity = "O(n^2)"
    elif visitor.max_loop_depth == 1:
        time_complexity = "O(n)"
    elif visitor.has_sort:
        time_complexity = "O(n log n)"
    else:
        time_complexity = "O(1)"

    has_collection_growth = any(
        isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.List, ast.Set, ast.Dict))
        for node in ast.walk(tree)
    )
    space_complexity = "O(n)" if has_collection_growth else "O(1)"
    return {
        "cyclomatic_complexity": 1 + visitor.branch_count,
        "cyclomatic_rating": _complexity_rating(1 + visitor.branch_count),
        "estimated_time_complexity": time_complexity,
        "estimated_space_complexity": space_complexity,
        "complexity_is_estimate": True,
    }


def _complexity_rating(value: int) -> str:
    if value <= 5:
        return "Low"
    if value <= 10:
        return "Moderate"
    if value <= 20:
        return "High"
    return "Very High"


def _score(issues: list[dict], complexity: dict) -> dict:
    category_scores = {"security": 100, "correctness": 100, "maintainability": 100, "readability": 100, "performance": 100}
    category_map = {
        "security": "security",
        "bug": "correctness",
        "correctness": "correctness",
        "maintainability": "maintainability",
        "readability": "readability",
    }
    for issue in issues:
        category = category_map.get(issue["category"])
        if category:
            category_scores[category] -= SEVERITY_PENALTIES[issue["severity"]]

    if complexity["cyclomatic_complexity"] > 5:
        category_scores["readability"] -= min(50, (complexity["cyclomatic_complexity"] - 5) * 5)
    if complexity["estimated_time_complexity"] == "O(n^2)":
        category_scores["performance"] -= 15
    elif complexity["estimated_time_complexity"] == "O(n^3+)":
        category_scores["performance"] -= 30

    for key in category_scores:
        category_scores[key] = max(0, category_scores[key])
    weights = {"security": 0.25, "correctness": 0.25, "maintainability": 0.2, "readability": 0.15, "performance": 0.15}
    overall = round(sum(category_scores[key] * weights[key] for key in weights))
    category_scores["overall"] = overall
    return category_scores


def analyze_python(code: str) -> dict:
    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        issue = {
            "type": "syntax_error",
            "severity": "HIGH",
            "title": "Python syntax error",
            "message": error.msg,
            "line": error.lineno,
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

    visitor = _AnalysisVisitor()
    visitor.visit(tree)
    seen: set[tuple[str, int | None]] = set()
    issues = []
    for issue in visitor.issues:
        signature = (issue["type"], issue["line"])
        if signature not in seen:
            seen.add(signature)
            issues.append(issue)
    metrics = _estimate_complexity(visitor, tree)
    metrics["quality_scores"] = _score(issues, metrics)
    return {"issues": issues, "metrics": metrics}
