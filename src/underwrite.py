from math import asin, cos, radians, sin, sqrt
from .mortgage import monthly_payment, remaining_balance


def haversine_miles(lat1, lon1, lat2, lon2):
    r = 3958.7613
    dlat, dlon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2*r*asin(sqrt(a))


def _owner_cost_for_price(price, listing, config, scenario_name="base"):
    f, c, h = config["financing"], config["monthly_costs"], config["house_hack"]
    down = price * float(f["down_payment_pct"])
    loan = price - down
    pi = monthly_payment(loan, float(f["mortgage_rate_pct"]), int(f["mortgage_term_years"]))
    tax = price * float(c["property_tax_annual_pct_of_price"]) / 12
    ins = float(c["homeowners_insurance_monthly"])
    pmi = 0 if float(f["down_payment_pct"]) >= .20 else loan * float(c["pmi_annual_pct_of_loan"]) / 12
    maint = price * float(c["maintenance_reserve_annual_pct_of_price"]) / 12
    hoa = float(listing.get("hoa_monthly") or c["hoa_default_monthly"])
    util = float(c["utilities_paid_by_owner_monthly"])
    rooms = min(max(0, int(listing["bedrooms"]) - int(h["owner_occupied_bedrooms"])), int(h["max_rooms_to_rent"]))
    gross_rent = rooms * float(h["default_room_rent_monthly"])
    return pi + tax + ins + pmi + maint + hoa + util - gross_rent


def max_price_for_target_owner_cost(listing, config, scenario_name="base"):
    target = float(config["financing"]["target_owner_monthly_cost"])
    low, high = 100000.0, 600000.0
    for _ in range(80):
        mid = (low + high) / 2
        if _owner_cost_for_price(mid, listing, config, scenario_name) <= target:
            low = mid
        else:
            high = mid
    return round(low, 2)


def underwrite(listing, config, scenario_name="base"):
    f, c, h, loc = config["financing"], config["monthly_costs"], config["house_hack"], config["location"]
    s = config["scenarios"][scenario_name]
    price = float(listing["price"])
    down = price * float(f["down_payment_pct"])
    loan = price - down
    pi = monthly_payment(loan, float(f["mortgage_rate_pct"]), int(f["mortgage_term_years"]))
    tax = price * float(c["property_tax_annual_pct_of_price"]) / 12
    pi_plus_tax = pi + tax
    ins = float(c["homeowners_insurance_monthly"])
    pmi = 0 if float(f["down_payment_pct"]) >= .20 else loan * float(c["pmi_annual_pct_of_loan"]) / 12
    maint = price * float(c["maintenance_reserve_annual_pct_of_price"]) / 12
    hoa = float(listing.get("hoa_monthly") or c["hoa_default_monthly"])
    util = float(c["utilities_paid_by_owner_monthly"])
    rooms = min(max(0, int(listing["bedrooms"]) - int(h["owner_occupied_bedrooms"])), int(h["max_rooms_to_rent"]))
    gross_rent = rooms * float(h["default_room_rent_monthly"])
    effective_rent = gross_rent * (1 - float(s["vacancy_pct"]))
    all_in = pi + tax + ins + pmi + maint + hoa + util

    # While the owner is living in the house, show the actual monthly cost assuming
    # the occupied rooms are paying rent. Vacancy-adjusted rent is kept separately
    # as a conservative stress-test metric.
    owner_cost = all_in - gross_rent
    conservative_owner_cost = all_in - effective_rent

    close = down + price*float(f["closing_cost_pct"]) + float(f["lender_points_dollars"]) - float(f["seller_credit_dollars"])
    gross_income = float(f["annual_gross_income"])/12
    dti = (float(f["existing_monthly_debt"]) + pi + tax + ins + pmi + hoa) / gross_income
    bal5 = remaining_balance(loan, float(f["mortgage_rate_pct"]), int(f["mortgage_term_years"]), 60)
    fv5 = price*((1+float(s["appreciation_pct"]))**5)
    dist = ""
    if listing.get("latitude") is not None and listing.get("longitude") is not None:
        dist = round(haversine_miles(float(listing["latitude"]), float(listing["longitude"]), float(loc["exit_130_latitude"]), float(loc["exit_130_longitude"])), 2)

    max_target_price = max_price_for_target_owner_cost(listing, config, scenario_name)
    discount_needed = max(0.0, price - max_target_price)

    return {**listing,
        "scenario": scenario_name, "down_payment": round(down,2), "loan_amount": round(loan,2),
        "mortgage_pi": round(pi,2), "property_tax_est": round(tax,2), "mortgage_pi_plus_tax": round(pi_plus_tax,2),
        "insurance_est": round(ins,2), "pmi_est": round(pmi,2), "maintenance_reserve": round(maint,2), "utilities_est": round(util,2),
        "all_in_monthly_cost": round(all_in,2), "rooms_rented": rooms,
        "gross_room_rent": round(gross_rent,2), "effective_room_rent": round(effective_rent,2),
        "owner_monthly_cost": round(owner_cost,2), "conservative_owner_monthly_cost": round(conservative_owner_cost,2),
        "target_owner_monthly_cost": round(float(f["target_owner_monthly_cost"]),2),
        "max_price_for_target_owner_cost": max_target_price, "discount_needed_for_target": round(discount_needed,2),
        "cash_to_close": round(close,2), "cash_after_close": round(float(f["available_cash"])-close,2), "dti_proxy_pct": round(dti*100,2),
        "straight_line_miles_to_exit_130": dist, "principal_paid_5y": round(loan-bal5,2),
        "future_value_5y": round(fv5,2), "equity_5y": round(fv5-bal5,2)}
