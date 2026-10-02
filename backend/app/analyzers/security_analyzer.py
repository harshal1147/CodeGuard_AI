from app.analyzers.base import Analyzer


class SecurityAnalyzer(Analyzer):
    name = "security"

    def analyze(self, code: str, metadata: dict | None = None) -> dict:
        issues = []
        lowered = code.lower()

        if "subprocess" in lowered or "os.system" in lowered:
            issues.append({"type": "command_injection", "severity": "HIGH", "line": 1, "message": "Potential command execution path detected."})
        if "password" in lowered or "api_key" in lowered or "secret" in lowered:
            issues.append({"type": "hardcoded_secret", "severity": "HIGH", "line": 1, "message": "Potential hardcoded secret or credential found."})
        if "eval(" in lowered:
            issues.append({"type": "injection_risk", "severity": "HIGH", "line": 1, "message": "Unsafe eval-like execution can enable script injection."})

        return {"issues": issues, "metrics": {"security_score": 80}}
