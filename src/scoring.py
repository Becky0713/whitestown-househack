def score(deal, config):
    m, loc, f, w = config["market"], config["location"], config["financing"], config["scoring"]
    pts, notes = 0, []

    bedrooms = int(deal["bedrooms"])
    if bedrooms >= int(m["preferred_bedrooms"]):
        pts += w["bedrooms_4_points"]
        notes.append("4BR priority")
    else:
        notes.append("3BR backup")

    if float(deal["price"]) <= float(m["target_max_purchase_price"]):
        pts += w["price_at_or_below_target_points"]
        notes.append("price<=target")

    pi_tax = float(deal["mortgage_pi_plus_tax"])
    if pi_tax <= float(f["ideal_pi_plus_tax_monthly"]):
        pts += w["pi_plus_tax_ideal_points"]
        notes.append("P&I+tax<=2100")
    elif pi_tax <= float(f["max_pi_plus_tax_monthly"]):
        pts += w["pi_plus_tax_under_max_points"]
        notes.append("P&I+tax<3000")
    else:
        pts -= w["pi_plus_tax_over_max_penalty"]
        notes.append("P&I+tax>3000")

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
        notes.append("owner cost<=800")
    else:
        pts -= w["owner_cost_over_target_penalty"]
        notes.append("owner cost>800")

    year = int(deal.get("year_built") or 0)
    if year >= 2000:
        pts += w["year_2000_plus_points"]
        notes.append("2000+")
    elif year >= 1990:
        pts += w["year_1990_1999_points"]
        notes.append("1990+")
    elif year >= 1980:
        pts += w["year_1980_1989_points"]
        notes.append("1980+")
    elif year and year < 1950:
        pts -= w["pre_1950_penalty"]
        notes.append("VERY OLD")
    elif year:
        pts -= w["pre_1980_penalty"]
        notes.append("OLDER HOME")

    if float(deal["equity_5y"]) > 0:
        pts += w["base_equity_positive_points"]
        notes.append("5Y equity positive")

    return int(pts), notes


def verdict(deal, config):
    f = config["financing"]
    bedrooms = int(deal["bedrooms"])
    pi_tax = float(deal["mortgage_pi_plus_tax"])
    owner_cost = float(deal["owner_monthly_cost"])
    reserve_ok = float(deal["cash_after_close"]) >= float(f["minimum_cash_reserve_after_close"])
    year = int(deal.get("year_built") or 0)

    if pi_tax > float(f["max_pi_plus_tax_monthly"]):
        return "REJECT"

    if bedrooms >= 4 and pi_tax <= float(f["ideal_pi_plus_tax_monthly"]) and owner_cost <= float(f["target_owner_monthly_cost"]) and reserve_ok and (year == 0 or year >= 1990):
        return "PRIORITY"

    if bedrooms >= 4 and owner_cost <= float(f["target_owner_monthly_cost"]) and reserve_ok:
        return "INVESTIGATE"

    if bedrooms == 3 and owner_cost <= float(f["target_owner_monthly_cost"]) and reserve_ok:
        return "3BR VALUE OPTION"

    if float(deal["discount_needed_for_target"]) <= 20000 and reserve_ok:
        return "WATCH / NEGOTIATE"

    return "REJECT"
