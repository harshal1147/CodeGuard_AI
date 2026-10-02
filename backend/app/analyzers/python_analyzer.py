from app.analyzers.base import Analyzer


class PythonAnalyzer(Analyzer):
    name = "python"

    def detect_language(self, code: str, filename: str | None = None) -> str:
        if filename and filename.endswith(".py"):
            return "python"
        return "python" if "def " in code or "import " in code else "unknown"

    def analyze(self, code: str, metadata: dict | None = None) -> dict:
        issues = []
        if "eval(" in code:
            issues.append({"type": "unsafe_eval", "severity": "HIGH", "line": 1, "message": "Potential unsafe use of eval()."})
        if "input(" in code and "password" in code.lower():
            issues.append({"type": "hardcoded_credential", "severity": "HIGH", "line": 1, "message": "Credential-like value appears in code."})
        return {"issues": issues, "metrics": {"cyclomatic_complexity": 3, "estimated_time": "O(n)", "estimated_space": "O(1)"}}
