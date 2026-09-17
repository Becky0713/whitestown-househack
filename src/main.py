import csv
from .config import ROOT, load_config
from .rentcast import fetch_sale_listings, normalize_listing
from .underwrite import underwrite
from .scoring import score


def passes_basic_filters(row, cfg):
    m = cfg["market"]
    if row["status"] and row["status"] != m["status"]: return False
    if not (m["min_list_price"] <= float(row["price"]) <= m["max_list_price"]): return False
    if not (m["min_bedrooms"] <= int(row["bedrooms"]) <= m["max_bedrooms"]): return False
    if float(row["bathrooms"]) < float(m["min_bathrooms"]): return False
    return True


def main():
    cfg = load_config()
    listings = [normalize_listing(x) for x in fetch_sale_listings(cfg)]
    listings = [x for x in listings if passes_basic_filters(x, cfg)]
    deals = []
    for listing in listings:
        deal = underwrite(listing, cfg, "base")
        pts, reasons = score(deal, cfg)
        deal["score"], deal["score_reasons"] = pts, "; ".join(reasons)
        deals.append(deal)
    deals.sort(key=lambda x: (-x["score"], x["owner_monthly_cost"], x["price"]))
    out = ROOT / "reports" / "shortlist.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    if deals:
        with out.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(deals[0].keys())); w.writeheader(); w.writerows(deals)
    else:
        out.write_text("", encoding="utf-8")
    print(f"Wrote {len(deals)} screened deals to {out}")


if __name__ == "__main__":
    main()
