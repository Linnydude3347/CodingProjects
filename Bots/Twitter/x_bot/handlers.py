from __future__ import annotations
import re
from typing import Optional

def find_keyword(text: str, keywords: list[str]) -> Optional[str]:
    if not keywords: return None
    t = text or ""
    for kw in keywords:
        if not kw: continue
        pattern = re.escape(kw)
        if re.search(rf"\b{pattern}\b", t, flags=re.IGNORECASE):
            return kw
    return None

def render_reply(template: str, *, author: str, keyword: str) -> str:
    return template.format(author=author or "", keyword=keyword or "")