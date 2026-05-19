from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Finding:
    pattern: str
    issue: str
    severity: str
    line: int
    code: str

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)
