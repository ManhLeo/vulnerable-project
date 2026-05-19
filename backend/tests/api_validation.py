import io
import json
from typing import Any

import requests


BASE_URL = "http://127.0.0.1:8000/api/v1"


def print_result(name: str, response: requests.Response) -> None:
    print(f"\n--- {name} ---")
    print("status_code:", response.status_code)
    print("body:", response.text)


def post_scan_code(payload: dict[str, Any], name: str) -> requests.Response:
    response = requests.post(f"{BASE_URL}/scan/code", json=payload, timeout=60)
    print_result(name, response)
    return response


def post_scan_file(
    file_name: str,
    file_content: bytes,
    language: str | None,
    name: str,
) -> requests.Response:
    files = {"file": (file_name, io.BytesIO(file_content), "application/octet-stream")}
    data = {}
    if language is not None:
        data["language"] = language
    response = requests.post(f"{BASE_URL}/scan/file", files=files, data=data, timeout=60)
    print_result(name, response)
    return response


def get_history(page: int, limit: int, name: str) -> requests.Response:
    response = requests.get(f"{BASE_URL}/scan/history", params={"page": page, "limit": limit}, timeout=60)
    print_result(name, response)
    return response


def main() -> None:
    # 1) /scan/code validation
    vuln_c = {
        "source_code": "#include <string.h>\nint main(){char buf[8]; strcpy(buf, \"AAAAAAAAAAAAAAAA\"); return 0;}",
        "language": "c",
    }
    vuln_py = {
        "source_code": "import os\nos.system(input())",
        "language": "py",
    }
    sqli_py = {
        "source_code": "query = \"SELECT * FROM users WHERE id=\" + user_input",
        "language": "py",
    }
    safe_py = {
        "source_code": "def add(a, b):\n    return a + b",
        "language": "py",
    }
    mixed_py = {
        "source_code": "def ok():\n    x = 1\nimport os\nos.system('ls')\nquery = \"SELECT * FROM t WHERE id=\" + user_input",
        "language": "py",
    }

    post_scan_code(vuln_c, "scan_code_vulnerable_c")
    post_scan_code(vuln_py, "scan_code_vulnerable_python")
    post_scan_code(sqli_py, "scan_code_sql_injection")
    post_scan_code(safe_py, "scan_code_safe_python")
    post_scan_code(mixed_py, "scan_code_mixed_python")
    post_scan_code({"source_code": "console.log(1)", "language": "js"}, "scan_code_unsupported_language")
    post_scan_code({"source_code": "", "language": "py"}, "scan_code_empty_source")

    malformed = requests.post(
        f"{BASE_URL}/scan/code",
        data="{bad_json",
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    print_result("scan_code_malformed_json", malformed)

    # 2) /scan/file validation
    post_scan_file("sample.py", b"import os\nos.system(input())", "py", "scan_file_valid")
    malformed_multipart = requests.post(f"{BASE_URL}/scan/file", data="invalid", timeout=60)
    print_result("scan_file_malformed_multipart", malformed_multipart)
    post_scan_file("sample.exe", b"MZ...", None, "scan_file_unsupported_extension")
    post_scan_file("empty.py", b"", "py", "scan_file_empty_file")
    post_scan_file("big.py", b"a" * (5 * 1024 * 1024 + 10), "py", "scan_file_oversized")

    # 3) /scan/history + pagination
    get_history(1, 5, "scan_history_page_1_limit_5")
    get_history(2, 2, "scan_history_page_2_limit_2")
    get_history(0, 10, "scan_history_invalid_page")

    # 4/5 persistence + response contract quick assertions (printed)
    history_resp = requests.get(f"{BASE_URL}/scan/history", params={"page": 1, "limit": 10}, timeout=60)
    print_result("scan_history_for_persistence_check", history_resp)
    try:
        data = history_resp.json()
        items = data.get("data", {}).get("items", [])
        print("\n--- persistence_summary ---")
        print("history_items_count:", len(items))
        if items:
            sample = items[0]
            for field in ["id", "filename", "language", "is_vulnerable", "confidence", "risk_level", "created_at"]:
                print(f"{field}_present:", field in sample)
    except Exception as exc:
        print("persistence_parse_error:", str(exc))


if __name__ == "__main__":
    main()
