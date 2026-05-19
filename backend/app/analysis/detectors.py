from __future__ import annotations

from app.analysis.findings import Finding
from app.analysis.patterns import PatternRule, get_pattern_rules
from app.analysis.severity import get_severity_for_pattern


def detect_findings(source_code: str, language: str) -> list[Finding]:
    rules = get_pattern_rules(language)
    lines = source_code.splitlines()
    findings: list[Finding] = []

    for line_no, line_text in enumerate(lines, start=1):
        for rule in rules:
            if rule.regex.search(line_text):
                findings.append(
                    Finding(
                        pattern=rule.pattern,
                        issue=rule.issue,
                        severity=get_severity_for_pattern(rule.pattern),
                        line=line_no,
                        code=line_text.strip(),
                    )
                )
    return findings


def count_findings_by_severity(findings: list[Finding]) -> dict[str, int]:
    counts: dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for finding in findings:
        if finding.severity in counts:
            counts[finding.severity] += 1
    return counts
