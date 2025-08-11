from bs4 import BeautifulSoup
import pdfplumber, json, re, datetime as dt
from sqlalchemy import text
from .db import ENGINE

def insert_entity(source_id, ent):
    with ENGINE.begin() as con:
        con.execute(text("""        INSERT INTO raw_entities(source_id, full_name, tckn, vkn, passport_no, birth_date, nationality, payload_json)
        VALUES(:sid,:fn,:t,:v,:p,:bd,:nat,:pl)
        """), dict(
            sid=source_id, fn=ent.get("full_name"),
            t=ent.get("tckn"), v=ent.get("vkn"), p=ent.get("passport_no"),
            bd=ent.get("birth_date"), nat=ent.get("nationality"),
            pl=json.dumps(ent)
        ))

def parse_html(source_id, path):
    with open(path,"rb") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    rows = soup.select("table tr")
    if rows:
        for tr in rows[1:]:
            tds = [td.get_text(strip=True) for td in tr.find_all("td")]
            if not tds: continue
            ent = {
                "full_name": tds[0] if len(tds)>0 else None,
                "tckn": re.sub(r"\D","", tds[1]) if len(tds)>1 else None,
                "passport_no": (tds[2] if len(tds)>2 else None) or None,
                "birth_date": None,
                "nationality": None
            }
            insert_entity(source_id, ent)
    else:
        # tablo yoksa metinden kaba çıkarım (kaynağa göre özelleştirilmeli)
        text = soup.get_text("\n", strip=True)
        for m in re.finditer(r"Ad(?:ı|i):\s*(.+?)\s+(TCKN|Pasaport):\s*([A-Z0-9]+)", text, re.I):
            ent={"full_name": m.group(1).strip()}
            if m.group(2).lower().startswith("tckn"):
                ent["tckn"] = re.sub(r"\D","", m.group(3))
            else:
                ent["passport_no"] = m.group(3)
            insert_entity(source_id, ent)

def parse_pdf(source_id, path):
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            for line in t.splitlines():
                m = re.search(r"Ad(?:ı|i)\s*:\s*(.+?)\s+(TCKN|Pasaport)\s*:\s*([A-Z0-9]+)", line, re.I)
                if m:
                    ent={"full_name": m.group(1).strip()}
                    if m.group(2).lower().startswith("tckn"):
                        ent["tckn"] = re.sub(r"\D","", m.group(3))
                    else:
                        ent["passport_no"] = m.group(3)
                    insert_entity(source_id, ent)
