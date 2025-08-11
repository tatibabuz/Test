import os, requests
from sqlalchemy import text
from .db import ENGINE

def send_slack(textmsg:str):
    url = os.getenv("SLACK_WEBHOOK_URL")
    if not url: return
    try:
        requests.post(url, json={"text": textmsg}, timeout=15)
    except Exception:
        pass

def daily_summary():
    with ENGINE.begin() as con:
        rows = con.execute(text("""        SELECT m.created_at, m.customer_id, w.id as watch_id
        FROM matches m
        JOIN watchlist_items w ON m.item_id=w.id
        WHERE m.created_at::date = CURRENT_DATE
        ORDER BY m.created_at DESC
        """)).fetchall()
    if rows:
        msg = "*Günlük MASAK eşleşmeleri*: " + str(len(rows))
        msg += "\n" + "\n".join([f"- {r.customer_id} (watch_id={r.watch_id})" for r in rows])
        send_slack(msg)
