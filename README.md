# Whitestown House-Hack Radar

A small underwriting + listing-screening project for an owner-occupied house hack in Whitestown, Indiana.

## Current buy box

- Target purchase timing: by February 2027, but only if the deal works on its own economics
- Search list price: **$230k–$320k**
- Target negotiated purchase price: **<= $300k**
- Property type: **single-family**
- Bedrooms: **3–4**, with 4 preferred
- Bathrooms: **2+ preferred**
- HOA: **<= $75/mo preferred**
- Access: **roughly <= 10 minutes to I-65 Exit 130 / Whitestown Pkwy preferred**
- Strategy: owner occupies one bedroom and rents 2–3 spare rooms
- Base case assumes **0% annual home-price appreciation**

The goal is not to predict that Whitestown will appreciate. The goal is to find a property that is still acceptable if appreciation is zero and treat any upside as a bonus.

## What the project does

1. Pulls active Whitestown sale listings from RentCast.
2. Applies the buy-box filters.
3. Estimates mortgage payment and all-in monthly housing cost.
4. Applies an owner-occupied room-rental house-hack assumption.
5. Calculates cash to close, monthly owner housing cost, DTI proxy, and 5-year equity.
6. Runs Bear / Base / Bull scenarios.
7. Saves daily listing snapshots and tracks price changes between runs.
8. Produces `reports/shortlist.csv` ranked by the configurable scoring model.

## Important limitations

This is a screening tool, not a substitute for lender, title, inspection, insurance, legal, tax, HOA, or MLS verification.

- RentCast is not the local MLS. Verify shortlisted properties in MIBOR / with a licensed agent before acting.
- Room-rent assumptions are manually configurable because whole-unit rental APIs do not reliably represent room rentals.
- Distance to I-65 is a straight-line proxy unless a routing API is added later.
- Indiana property tax estimates in this model are underwriting assumptions, not parcel-level tax quotes.
- Do not commit API keys. Use `.env` locally.

## Quick start

### 1. Create a RentCast API key

https://developers.rentcast.io/reference/introduction

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure credentials

```bash
cp .env.example .env
```

Then put your key in `.env`:

```text
RENTCAST_API_KEY=...
```

### 4. Run the radar

```bash
python -m src.main
```

Outputs:

- `data/raw/YYYY-MM-DD_sale_listings.csv`
- `data/processed/listing_history.csv`
- `reports/shortlist.csv`
- `reports/latest_summary.txt`

## Main assumptions

Edit `config/criteria.yaml` rather than editing Python code.

Most important fields:

- purchase price range
- down-payment percentage
- mortgage interest rate
- closing-cost percentage
- points / lender fees
- property-tax assumption
- insurance
- PMI
- maintenance reserve
- utilities paid by owner
- room rent
- vacancy
- minimum cash reserve after closing

This makes it easy to compare today's rate with a lower-rate scenario later without rebuilding the model.

## Wait vs. buy logic

The model deliberately separates rate and purchase price. A lower mortgage rate is not automatically a better deal if prices rise at the same time.

Use `src/wait_vs_buy.py` to compare two scenarios:

```bash
python -m src.wait_vs_buy \
  --buy-now-price 270000 --buy-now-rate 7.13 \
  --wait-price 290000 --wait-rate 6.20
```

The script compares monthly P&I, all-in owner cost, cash to close, and 5-year equity under the same house-hack assumptions.

## Verification workflow for any shortlisted property

Before making an offer:

1. Confirm active/pending/sold status and MLS facts.
2. Read seller disclosures.
3. Verify HOA dues and rental / roommate restrictions.
4. Verify parcel-level property tax.
5. Obtain a homeowners-insurance quote.
6. Obtain a lender Loan Estimate with rate, APR, points, PMI, and total cash to close.
7. Inspect roof, HVAC, foundation, plumbing, electrical, and water intrusion risk.
8. Validate room-rent demand and parking / bathroom practicality.

## Repository structure

```text
config/criteria.yaml          investment assumptions and buy box
src/rentcast.py               RentCast API client
src/mortgage.py               mortgage / amortization math
src/underwrite.py             property underwriting
src/history.py                snapshot + price-change tracking
src/scoring.py                shortlist scoring
src/main.py                   end-to-end run
src/wait_vs_buy.py            compare buying now vs waiting
models/                       Excel model (when present)
data/raw/                     daily snapshots (gitignored)
data/processed/               history file (gitignored)
reports/                      generated shortlist / summaries (gitignored)
```
