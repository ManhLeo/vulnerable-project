from __future__ import annotations

import re


def preprocess_source_code(source_code: str, max_chars: int = 10000) -> str:
    """
    Mandatory preprocessing pipeline:
    raw source code
    -> normalize whitespace
    -> remove excessive empty lines
    -> truncate safely
    """
    text = source_code.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    if len(text) > max_chars:
        text = text[:max_chars]

    return text
