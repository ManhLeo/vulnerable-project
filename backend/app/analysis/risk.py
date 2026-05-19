from __future__ import annotations

from app.analysis.detectors import count_findings_by_severity
from app.analysis.findings import Finding
from app.analysis.severity import SEVERITY_WEIGHTS


def calculate_risk_score(confidence: float, findings: list[Finding]) -> float:
    safe_confidence = max(0.0, min(confidence, 1.0))
    if not findings:
        return round(safe_confidence * 0.4, 4)

    severity_counts = count_findings_by_severity(findings)
    weighted_findings = (
        severity_counts["CRITICAL"] * SEVERITY_WEIGHTS["CRITICAL"]
        + severity_counts["HIGH"] * SEVERITY_WEIGHTS["HIGH"]
        + severity_counts["MEDIUM"] * SEVERITY_WEIGHTS["MEDIUM"]
        + severity_counts["LOW"] * SEVERITY_WEIGHTS["LOW"]
    )

    finding_count_bonus = min(len(findings) * 0.03, 0.30)
    score = safe_confidence * 0.55 + weighted_findings + finding_count_bonus
    return round(max(0.0, min(score, 1.0)), 4)


def classify_risk_level(risk_score: float, findings: list[Finding] | None = None) -> str:
    findings = findings or []
    severity_counts = count_findings_by_severity(findings)

    # Severity floor to avoid contradictory output:
    # any CRITICAL/HIGH finding must result in HIGH risk at minimum.
    if severity_counts["CRITICAL"] > 0 or severity_counts["HIGH"] > 0:
        return "HIGH"
    if severity_counts["MEDIUM"] > 0:
        return "MEDIUM"
    if severity_counts["LOW"] > 0:
        return "LOW"

    if risk_score >= 0.85:
        return "HIGH"
    if risk_score >= 0.60:
        return "MEDIUM"
    return "LOW"
