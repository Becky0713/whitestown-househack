import csv
from datetime import date


def _write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


def write_snapshot(rows, root):
    path = root / "data" / "raw" / f"{date.today().isoformat()}_sale_listings.csv"
    _write_csv(path, rows)
    return path


def update_history(rows, root):
    path = root / "data" / "processed" / "listing_history.csv"
    prior = {}
    if path.exists():
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f): prior[row["listing_id"]] = row
    today = date.today().isoformat()
    output = []
    for row in rows:
        lid = str(row["listing_id"])
        old = prior.get(lid)
        prev = float(old["current_price"]) if old and old.get("current_price") else float(row["price"])
        cur = float(row["price"])
        output.append({"listing_id": lid, "address": row["address"], "first_seen": old.get("first_seen", today) if old else today,
                       "last_seen": today, "previous_price": prev, "current_price": cur, "price_change": cur-prev,
                       "status": row.get("status", ""), "mls_number": row.get("mls_number", "")})
    _write_csv(path, output)
    return path
