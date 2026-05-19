from __future__ import annotations

from typing import Final


SEVERITY_WEIGHTS: Final[dict[str, float]] = {
    "CRITICAL": 0.40,
    "HIGH": 0.30,
    "MEDIUM": 0.20,
    "LOW": 0.10,
}

PATTERN_SEVERITY: Final[dict[str, str]] = {
    # C/C++
    "strcpy": "HIGH",
    "strcat": "HIGH",
    "gets": "CRITICAL",
    "sprintf": "HIGH",
    'scanf("%s")': "HIGH",
    "system": "CRITICAL",
    "memcpy": "MEDIUM",
    # Python
    "eval": "CRITICAL",
    "exec": "CRITICAL",
    "pickle.loads": "CRITICAL",
    "os.system": "CRITICAL",
    "subprocess(shell=True)": "CRITICAL",
    # SQL
    "sql_concat": "HIGH",
    "sql_fstring": "HIGH",
}


def get_severity_for_pattern(pattern: str) -> str:
    return PATTERN_SEVERITY.get(pattern, "LOW")
