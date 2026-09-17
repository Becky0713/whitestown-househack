def monthly_payment(principal, annual_rate_pct, term_years):
    if principal <= 0: return 0.0
    n = term_years * 12
    r = annual_rate_pct / 100 / 12
    if r == 0: return principal / n
    f = (1 + r) ** n
    return principal * r * f / (f - 1)


def remaining_balance(principal, annual_rate_pct, term_years, payments_made):
    if principal <= 0: return 0.0
    n = term_years * 12
    k = min(max(payments_made, 0), n)
    r = annual_rate_pct / 100 / 12
    if r == 0: return max(0.0, principal * (1 - k / n))
    pmt = monthly_payment(principal, annual_rate_pct, term_years)
    return max(0.0, principal * (1+r)**k - pmt * (((1+r)**k - 1)/r))
