from __future__ import annotations

from typing import Any

from app.analysis.detectors import count_findings_by_severity, detect_findings
from app.analysis.findings import Finding
from app.analysis.risk import calculate_risk_score, classify_risk_level


class FindingsMetricsService:
    """Rule-based static analysis that never touches the AI model stack."""

    def analyze(self, *, source_code: str, language: str, base_confidence: float = 0.0) -> dict[str, Any]:
        findings = detect_findings(source_code=source_code, language=language)
        risk_score = calculate_risk_score(base_confidence, findings)
        risk_level = classify_risk_level(risk_score, findings)
        severity_counts = count_findings_by_severity(findings)
        is_vulnerable = risk_score >= 0.40 or severity_counts["MEDIUM"] > 0

        return {
            "is_vulnerable_by_metrics": is_vulnerable,
            "findings_count": len(findings),
            "suspicious_patterns": [finding.to_dict() for finding in findings],
            "risk_score": risk_score,
            "risk_level": risk_level,
            "severity_counts": {
                "critical": severity_counts["CRITICAL"],
                "high": severity_counts["HIGH"],
                "medium": severity_counts["MEDIUM"],
                "low": severity_counts["LOW"],
            },
            "findings": findings,
        }

    @staticmethod
    def confidence_from_metrics(*, risk_score: float, risk_level: str, findings: list[Finding]) -> float:
        if risk_score >= 0.70 or risk_level.upper() in {"HIGH", "CRITICAL"}:
            return 0.85
        if risk_score >= 0.40 or risk_level.upper() == "MEDIUM":
            return 0.70
        if findings:
            return 0.60
        return 0.65


findings_metrics_service = FindingsMetricsService()
