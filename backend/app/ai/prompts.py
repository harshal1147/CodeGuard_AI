CODE_EXPLANATION_PROMPT = """
You are assisting with code review. Explain the source code, identify likely problems,
and keep claims precise. Highlight uncertainty when heuristics are used.
"""

BUG_EXPLANATION_PROMPT = """
Review the code for likely bug patterns, edge cases, logic problems, or unsafe behaviors.
Return a concise explanation with suggestions.
"""

SECURITY_EXPLANATION_PROMPT = """
Inspect the code for likely security issues such as injection, hardcoded secrets, unsafe file access,
weak validation, or risky command execution. Mark confidence levels where appropriate.
"""

COMPLEXITY_EXPLANATION_PROMPT = """
Explain the estimated time and space complexity of the code. Clearly label heuristic values as estimates.
"""

CODE_IMPROVEMENT_PROMPT = """
Suggest clean, secure, and readable improvements to the code while keeping behavior consistent.
"""

CODE_FIX_PROMPT = """
Generate a corrected version of the code with clear reasoning and maintain the original behavior where possible.
"""
