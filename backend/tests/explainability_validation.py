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
        "vulnerable_c_gets",
        '#include <stdio.h>\nint main(){char buf[8]; gets(buf); return 0;}',
        "c",
    )
    run_case(
        "sql_injection_pattern_cpp",
        '#include <string>\n#include <sqlite3.h>\nvoid query(std::string name) {\n    std::string q = "SELECT * FROM users WHERE name=\'" + name + "\'";\n}',
        "cpp",
    )
    run_case(
        "safe_c_add",
        "int add(int a, int b){\n    return a+b;\n}",
        "c",
    )


if __name__ == "__main__":
    main()
