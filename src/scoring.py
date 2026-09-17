def score(deal, config):
    m, loc, f, w = config["market"], config["location"], config["financing"], config["scoring"]
    pts, notes = 0, []
    if int(deal["bedrooms"]) >= int(m["preferred_bedrooms"]): pts += w["bedrooms_4_points"]; notes.append("4BR+")
    if float(deal["price"]) <= float(m["target_max_purchase_price"]): pts += w["price_at_or_below_target_points"]; notes.append("price<=target")
    if float(deal.get("hoa_monthly") or 0) <= float(m["max_hoa_monthly"]): pts += w["hoa_ok_points"]; notes.append("HOA ok")
    dist = deal.get("straight_line_miles_to_exit_130")
    if dist != "" and float(dist) <= float(loc["preferred_max_straight_line_miles"]): pts += w["distance_ok_points"]; notes.append("I-65 proxy ok")
    if float(deal["cash_after_close"]) >= float(f["minimum_cash_reserve_after_close"]): pts += w["cash_reserve_ok_points"]; notes.append("reserve ok")
    owner_cost = float(deal["owner_monthly_cost"])
    if owner_cost <= 700: pts += w["owner_cost_under_700_points"]; notes.append("owner cost<=700")
    elif owner_cost <= 1000: pts += w["owner_cost_under_1000_points"]; notes.append("owner cost<=1000")
    if float(deal["equity_5y"]) > 0: pts += w["base_equity_positive_points"]; notes.append("5Y equity positive")
    return int(pts), notes
