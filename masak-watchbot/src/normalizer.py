import re

def norm_name(s:str) -> str:
    s = re.sub(r"\s+"," ", s or "").strip()
    return s.upper()
