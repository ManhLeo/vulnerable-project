from app.analysis.detectors import detect_findings
from app.analysis.risk import calculate_risk_score, classify_risk_level


def run_case(name: str, code: str, language: str, confidence: float = 0.9) -> None:
    findings = detect_findings(code, language)
    print(f"\n--- {name} ---")
    print("findings_count:", len(findings))
    for finding in findings:
        print(finding.to_dict())
    score = calculate_risk_score(confidence, findings)
    level = classify_risk_level(score)
    print("risk_score:", score)
    print("risk_level:", level)


def main() -> None:
    run_case(
        "vulnerable_c_strcpy",
        '#include <string.h>\nint main(){char buf[8]; strcpy(buf, "AAAAAAAAAAAAAAAA"); return 0;}',
        "c",
    )
    run_case(
        "vulnerable_python_os_system",
        "import os\nos.system(input())",
        "py",
    )
    run_case(
        "sql_injection_pattern",
        'query = "SELECT * FROM users WHERE id=" + user_input',
        "py",
    )
    run_case(
        "mixed_python",
        'def ok():\n    x=1\nimport os\nos.system("ls")\nquery = "SELECT * FROM t WHERE id=" + user_input',
        "py",
    )
    run_case(
        "safe_python",
        "def add(a,b):\n    return a+b",
        "py",
    )


if __name__ == "__main__":
    main()
