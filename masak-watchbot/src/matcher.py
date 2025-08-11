from sqlalchemy import text
from rapidfuzz import fuzz
from .db import ENGINE
from .normalizer import norm_name

def load_customers():
    with ENGINE.begin() as con:
        rows = con.execute(text("""        SELECT customer_id, full_name, tckn, passport_no, birth_date
        FROM your_customers
        """)).fetchall()
    return [dict(r._mapping) for r in rows]

def save_match(cust, ent, method, score):
    from sqlalchemy import text
    with ENGINE.begin() as con:
        item_id = con.execute(text("""          INSERT INTO watchlist_items(raw_entity_id, status, first_seen, last_seen, fingerprint)
          VALUES(:rid,'active', NOW(), NOW(), :fp) RETURNING id
        """), {"rid": ent["id"], "fp": f"{ent['full_name']}|{ent.get('tckn')}|{ent.get('passport_no')}"}
        ).scalar_one()
        con.execute(text("""          INSERT INTO matches(customer_id, item_id, method, score, matched_fields_json)
          VALUES(:cid,:iid,:m,:s,:mf)
        """), {"cid": cust["customer_id"], "iid": item_id, "m": method, "s": int(score),
               "mf": '{"by":"%s"}' % method})

def run_matching():
    customers = load_customers()
    by_tckn = {c["tckn"]: c for c in customers if c.get("tckn")}
    by_pass = {c["passport_no"]: c for c in customers if c.get("passport_no")}

    with ENGINE.begin() as con:
        ents = con.execute(text("""        SELECT id, full_name, tckn, passport_no, birth_date
        FROM raw_entities
        WHERE id NOT IN (SELECT raw_entity_id FROM watchlist_items)
        """)).fetchall()

    for e in ents:
        em = dict(e._mapping)
        # Exact ID match
        if em.get("tckn") and em["tckn"] in by_tckn:
            save_match(by_tckn[em["tckn"]], em, "id_exact", 100)
            continue
        if em.get("passport_no") and em["passport_no"] in by_pass:
            save_match(by_pass[em["passport_no"]], em, "id_exact", 100)
            continue

        # Fuzzy by name (+ optional DOB equality)
        best = None
        for c in customers:
            if not c.get("full_name"): continue
            s = fuzz.token_sort_ratio(norm_name(c["full_name"]), norm_name(em.get("full_name","")))
            if s >= 92 and (not em.get("birth_date") or c.get("birth_date") == em.get("birth_date")):
                if not best or s > best[0]: best = (s, c)
        if best:
            save_match(best[1], em, "name_fuzzy", best[0])
