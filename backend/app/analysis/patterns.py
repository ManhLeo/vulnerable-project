from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class PatternRule:
    pattern: str
    issue: str
    regex: re.Pattern[str]


C_CPP_RULES: Final[list[PatternRule]] = [
    PatternRule("strcpy", "Potential buffer overflow", re.compile(r"\bstrcpy\s*\(")),
    PatternRule("strcat", "Potential buffer overflow", re.compile(r"\bstrcat\s*\(")),
    PatternRule("gets", "Unsafe input function", re.compile(r"\bgets\s*\(")),
    PatternRule("sprintf", "Potential format/string overflow", re.compile(r"\bsprintf\s*\(")),
    PatternRule('scanf("%s")', "Unbounded input read", re.compile(r"\bscanf\s*\(\s*\"%s")),
    PatternRule("system", "Potential command injection", re.compile(r"\bsystem\s*\(")),
    PatternRule("memcpy", "Potential unsafe memory copy", re.compile(r"\bmemcpy\s*\(")),
]

SQL_RULES: Final[list[PatternRule]] = [
    PatternRule(
        "sql_concat",
        "Possible SQL injection via string concatenation",
        re.compile(
            r"(?i)\b(SELECT|INSERT|UPDATE|DELETE)\b.*(\+|%|\.(format)\s*\()"
        ),
    ),
    PatternRule(
        "sql_fstring",
        "Possible SQL injection via f-string construction",
        re.compile(r"(?i)f[\"']\s*(SELECT|INSERT|UPDATE|DELETE)\b"),
    ),
]


def get_pattern_rules(language: str) -> list[PatternRule]:
    normalized = language.strip().lower()
    if normalized in {"c", "cpp", "c++", "h", "hpp"}:
        return [*C_CPP_RULES, *SQL_RULES]
    return []
