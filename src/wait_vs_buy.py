import argparse
from copy import deepcopy
from .config import load_config
from .underwrite import underwrite


def run_case(label, price, rate, cfg):
    local = deepcopy(cfg)
    local["financing"]["mortgage_rate_pct"] = rate
    listing = {"listing_id": label, "status": "Scenario", "address": label, "price": price,
               "bedrooms": 4, "bathrooms": 2.5, "square_footage": 0, "year_built": 0,
               "property_type": "Single Family", "days_on_market": 0, "hoa_monthly": 0,
               "latitude": None, "longitude": None, "mls_name": "", "mls_number": ""}
    return underwrite(listing, local, "base")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--buy-now-price", type=float, required=True)
    p.add_argument("--buy-now-rate", type=float, required=True)
    p.add_argument("--wait-price", type=float, required=True)
    p.add_argument("--wait-rate", type=float, required=True)
    a = p.parse_args()
    cfg = load_config()
    now = run_case("Buy now", a.buy_now_price, a.buy_now_rate, cfg)
    wait = run_case("Wait", a.wait_price, a.wait_rate, cfg)
    rows = [("Purchase price","price"),("Mortgage P&I / mo","mortgage_pi"),("All-in housing / mo","all_in_monthly_cost"),
            ("Effective room rent / mo","effective_room_rent"),("Owner housing cost / mo","owner_monthly_cost"),
            ("Cash to close","cash_to_close"),("Cash after close","cash_after_close"),("5Y principal paid","principal_paid_5y"),
            ("5Y equity (0% appreciation)","equity_5y")]
    print(f'{"Metric":34} {"Buy now":>15} {"Wait":>15} {"Wait - Now":>15}')
    print("-"*84)
    for label,key in rows:
        x,y=float(now[key]),float(wait[key])
        print(f"{label:34} ${x:>13,.0f} ${y:>13,.0f} ${y-x:>13,.0f}")


if __name__ == "__main__":
    main()
