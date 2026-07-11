from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from app.core.exceptions import NotFoundException


_DEMO_SAMPLES: dict[str, dict[str, Any]] = {
    "unsafe_strcpy": {
        "id": "unsafe_strcpy",
        "title": "Unsafe strcpy example",
        "language": "c",
        "description": "Example of unsafe string copy into a fixed-size buffer.",
        "source_code": """#include <stdio.h>
#include <string.h>

void copy_input(const char *input) {
    char buffer[8];
    strcpy(buffer, input);
    printf("%s\\n", buffer);
}

int main() {
    copy_input("this input is too long");
    return 0;
}
""",
        "result": {
            "is_vulnerable": True,
            "confidence": 0.94,
            "risk_level": "HIGH",
            "findings": [
                {
                    "pattern": "unsafe_strcpy",
                    "issue": "Unsafe copy without bounds checking",
                    "severity": "HIGH",
                    "line": 6,
                    "code": "strcpy(buffer, input);",
                    "description": "strcpy can overflow buffer when input length exceeds destination size.",
                    "recommendation": "Use a bounded copy routine and validate input length before copying.",
                }
            ],
        },
    },
    "safe_bounds_check": {
        "id": "safe_bounds_check",
        "title": "Bounds checked copy",
        "language": "c",
        "description": "Example of bounded copy with explicit null termination.",
        "source_code": """#include <stdio.h>
#include <string.h>

void copy_input(const char *input) {
    char buffer[16];
    strncpy(buffer, input, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\\0';
    printf("%s\\n", buffer);
}

int main() {
    copy_input("hello");
    return 0;
}
""",
        "result": {
            "is_vulnerable": False,
            "confidence": 0.88,
            "risk_level": "LOW",
            "findings": [],
        },
    },
}


class DemoScanService:
    """Precomputed demo scans. This service intentionally never calls AI inference."""

    def list_samples(self) -> list[dict[str, Any]]:
        return [
            {
                "id": sample["id"],
                "title": sample["title"],
                "language": sample["language"],
                "source_code": sample["source_code"],
                "description": sample["description"],
            }
            for sample in _DEMO_SAMPLES.values()
        ]

    def scan_sample(self, sample_id: str) -> dict[str, Any]:
        sample = _DEMO_SAMPLES.get(sample_id)
        if sample is None:
            raise NotFoundException(
                message="Demo sample not found",
                error_code="DEMO_SAMPLE_NOT_FOUND",
            )

        result = deepcopy(sample["result"])
        return {
            "scan_id": f"demo-{sample['id']}",
            "is_demo": True,
            "source_type": "demo",
            "language": sample["language"],
            "source_code": sample["source_code"],
            "is_vulnerable": result["is_vulnerable"],
            "confidence": result["confidence"],
            "risk_level": result["risk_level"],
            "findings": result["findings"],
            "metadata": {
                "model_name": "Demo Precomputed Result",
                "model_mode": "demo",
                "selected_checkpoint": None,
                "inference_used": False,
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        }


demo_scan_service = DemoScanService()
