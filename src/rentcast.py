import os
import requests
from dotenv import load_dotenv

SALE_URL = "https://api.rentcast.io/v1/listings/sale"


class RentCastError(RuntimeError):
    pass


def fetch_sale_listings(config):
    load_dotenv()
    key = os.getenv("RENTCAST_API_KEY", "").strip()
    if not key:
        raise RentCastError(
            "No RentCast API key was found. Double-click Run House Hack.command again "
            "and paste your key when asked."
        )

    m = config["market"]
    params = {
        "city": m["city"],
        "state": m["state"],
        "propertyType": m["property_type"],
        "bedrooms": f'{m["min_bedrooms"]}:{m["max_bedrooms"]}',
        "price": f'{m["min_list_price"]}:{m["max_list_price"]}',
        "limit": 500,
    }

    try:
        r = requests.get(
            SALE_URL,
            params=params,
            headers={"X-Api-Key": key, "Accept": "application/json"},
            timeout=30,
        )
    except requests.RequestException as exc:
        raise RentCastError(f"Could not reach RentCast: {exc}") from exc

    if r.status_code == 401:
        raise RentCastError(
            "RentCast rejected the API key (401). Check that you copied the full key correctly."
        )

    if r.status_code == 403:
        detail = ""
        try:
            payload = r.json()
            detail = payload.get("message") or payload.get("error") or ""
        except ValueError:
            pass
        extra = f"\nRentCast says: {detail}" if detail else ""
        raise RentCastError(
            "RentCast returned 403 Forbidden. This usually means the API key does not have an "
            "active API subscription (including the free Developer plan), or the key has a "
            "restriction blocking this request. Open https://app.rentcast.io/app/api and make "
            "sure the Developer API plan is active, then run this program again."
            + extra
        )

    if r.status_code == 429:
        raise RentCastError(
            "RentCast rate limit reached (429). Wait a little and try again."
        )

    if not r.ok:
        detail = r.text[:500]
        raise RentCastError(
            f"RentCast request failed with HTTP {r.status_code}.\n{detail}"
        )

    return r.json()


def normalize_listing(item):
    hoa = item.get("hoa") or {}
    return {
        "listing_id": item.get("id") or item.get("mlsNumber") or item.get("formattedAddress", ""),
        "status": item.get("status", ""),
        "address": item.get("formattedAddress", ""),
        "price": item.get("price") or 0,
        "bedrooms": item.get("bedrooms") or 0,
        "bathrooms": item.get("bathrooms") or 0,
        "square_footage": item.get("squareFootage") or 0,
        "year_built": item.get("yearBuilt") or 0,
        "property_type": item.get("propertyType", ""),
        "days_on_market": item.get("daysOnMarket") or 0,
        "hoa_monthly": hoa.get("fee") or 0,
        "latitude": item.get("latitude"),
        "longitude": item.get("longitude"),
        "mls_name": item.get("mlsName", ""),
        "mls_number": item.get("mlsNumber", ""),
    }
