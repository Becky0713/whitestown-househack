import os
import requests
from dotenv import load_dotenv

SALE_URL = "https://api.rentcast.io/v1/listings/sale"


def fetch_sale_listings(config):
    load_dotenv()
    key = os.getenv("RENTCAST_API_KEY", "").strip()
    if not key:
        raise RuntimeError("RENTCAST_API_KEY is missing. Copy .env.example to .env and add your key.")
    m = config["market"]
    params = {
        "city": m["city"], "state": m["state"], "propertyType": m["property_type"],
        "bedrooms": f'{m["min_bedrooms"]}:{m["max_bedrooms"]}',
        "price": f'{m["min_list_price"]}:{m["max_list_price"]}', "limit": 500,
    }
    r = requests.get(SALE_URL, params=params, headers={"X-Api-Key": key}, timeout=30)
    r.raise_for_status()
    return r.json()


def normalize_listing(item):
    hoa = item.get("hoa") or {}
    return {
        "listing_id": item.get("id") or item.get("mlsNumber") or item.get("formattedAddress", ""),
        "status": item.get("status", ""), "address": item.get("formattedAddress", ""),
        "price": item.get("price") or 0, "bedrooms": item.get("bedrooms") or 0,
        "bathrooms": item.get("bathrooms") or 0, "square_footage": item.get("squareFootage") or 0,
        "year_built": item.get("yearBuilt") or 0, "property_type": item.get("propertyType", ""),
        "days_on_market": item.get("daysOnMarket") or 0, "hoa_monthly": hoa.get("fee") or 0,
        "latitude": item.get("latitude"), "longitude": item.get("longitude"),
        "mls_name": item.get("mlsName", ""), "mls_number": item.get("mlsNumber", ""),
    }
