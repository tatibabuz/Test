from .db import ensure_schema
from .fetchers import fetch_all
from .parsers import parse_html, parse_pdf
from .matcher import run_matching
from .notify import daily_summary

def run():
    ensure_schema()
    docs = fetch_all()
    for sid, path, ftype, is_new in docs:
        if not is_new: continue
        if ftype == "html":
            parse_html(sid, path)
        else:
            parse_pdf(sid, path)
    run_matching()
    daily_summary()

if __name__ == "__main__":
    run()
