def score(deal, config):
    m, loc, f, w = config["market"], config["location"], config["financing"], config["scoring"]
    pts, notes = 0, []

    if int(deal["bedrooms"]) >= int(m["preferred_bedrooms"]):
        pts += w["bedrooms_4_points"]
        notes.append("4BR+")

    if float(deal["price"]) <= float(m["target_max_purchase_price"]):
        pts += w["price_at_or_below_target_points"]
        notes.append("price<=target")

    hoa = float(deal.get("hoa_monthly") or 0)
    if hoa <= float(m["max_hoa_monthly"]):
        pts += w["hoa_ok_points"]
        notes.append("HOA ok")
    else:
        pts -= w["hoa_over_limit_penalty"]
        notes.append("HIGH HOA")

    dist = deal.get("straight_line_miles_to_exit_130")
    if dist != "" and float(dist) <= float(loc["preferred_max_straight_line_miles"]):
        pts += w["distance_ok_points"]
        notes.append("I-65 proxy ok")

    if float(deal["cash_after_close"]) >= float(f["minimum_cash_reserve_after_close"]):
        pts += w["cash_reserve_ok_points"]
        notes.append("reserve ok")
    else:
        pts -= w["cash_reserve_short_penalty"]
        notes.append("LOW RESERVE")

    if float(deal["owner_monthly_cost"]) <= float(f["target_owner_monthly_cost"]):
        pts += w["owner_cost_at_or_below_target_points"]
        notes.append("owner cost<=target")
    else:
        pts -= w["owner_cost_over_target_penalty"]
        notes.append("OWNER COST TOO HIGH")

    year = int(deal.get("year_built") or 0)
    if year >= 2000:
        pts += w["year_2000_plus_points"]
        notes.append("2000+")
    elif year >= int(m["preferred_min_year_built"]):
        pts += w["year_1980_1999_points"]
        notes.append("1980+")
    elif year and year < 1950:
        pts -= w["pre_1950_penalty"]
        notes.append("VERY OLD")
    elif year:
        pts -= w["year_1950_1979_penalty"]
        notes.append("OLDER HOME")

    if float(deal["equity_5y"]) > 0:
        pts += w["base_equity_positive_points"]
        notes.append("5Y equity positive")

    return int(pts), notes


def verdict(deal, config):
    f = config["financing"]
    owner_ok = float(deal["owner_monthly_cost"]) <= float(f["target_owner_monthly_cost"])
    reserve_ok = float(deal["cash_after_close"]) >= float(f["minimum_cash_reserve_after_close"])

    if owner_ok and reserve_ok:
        return "INVESTIGATE"
    if float(deal["discount_needed_for_target"]) <= 20000 and reserve_ok:
        return "WATCH / NEGOTIATE"
    return "REJECT"
