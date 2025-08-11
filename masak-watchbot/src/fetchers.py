import hashlib, os, requests, time
from bs4 import BeautifulSoup
from sqlalchemy import text
from .db import ENGINE

# TODO: Gerçek MASAK kaynak URL'lerini ekleyin
MASAK_URLS = [
    "https://masak.hmb.gov.tr/5-maddeye-iliskin-bakanlar-kurulu-kararlari"
    "https://masak.hmb.gov.tr/6-maddeye-iliskin-bakanlar-kurulu-kararlari"
    
]

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def save_source(url, content, filetype):
    sha = sha256_bytes(content)
    name = f"{int(time.time())}_{sha[:10]}.{filetype}"
    path = os.path.join("/tmp", name)
    with open(path, "wb") as f: f.write(content)

    with ENGINE.begin() as con:
        existing = con.execute(text(
          "SELECT id FROM source_documents WHERE sha256=:s"), {"s": sha}
        ).fetchone()
        if existing: return existing[0], path, False
        rid = con.execute(text(
          "INSERT INTO source_documents(url, sha256, filetype, local_name) "
          "VALUES(:u,:s,:t,:n) RETURNING id"),
          {"u": url, "s": sha, "t": filetype, "n": name}
        ).scalar_one()
    return rid, path, True

def fetch_all():
    results = []
    for url in MASAK_URLS:
        r = requests.get(url, timeout=30)
        ct = (r.headers.get("Content-Type") or "").lower()
        if "pdf" in ct or url.lower().endswith(".pdf"):
            rid, path, is_new = save_source(url, r.content, "pdf")
            results.append((rid, path, "pdf", is_new))
        else:
            rid, path, is_new = save_source(url, r.content, "html")
            results.append((rid, path, "html", is_new))
    return results
