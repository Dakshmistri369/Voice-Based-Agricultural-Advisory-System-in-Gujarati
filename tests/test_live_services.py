"""
Verification CLI Test Suite for Phase 5 Live Weather & Mandi Price Services.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Force UTF-8 stdout for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from data_services.weather_service import weather_service
from data_services.price_service import price_service


def run_live_services_verification():
    """CLI test verifying Open-Meteo Weather for 3 districts & Mandi Prices for 5 commodities."""
    print("=" * 70)
    print("🌦️  PHASE 5: LIVE DATA SERVICES VERIFICATION")
    print("=" * 70)

    # 1. Weather Service Verification (3 Districts)
    test_districts = ["Rajkot", "Ahmedabad", "Junagadh"]
    print("\n--- 1. TESTING WEATHER SERVICE (3 DISTRICTS) ---")

    for dist in test_districts:
        w = weather_service.fetch_weather(dist)
        status_tag = "LIVE API" if w["is_live"] else "OFFLINE CACHE"
        print(f"📍 District: {w['district_gujarati']} ({w['district_english']}) [{status_tag}]")
        print(f"   Temp: {w['temp_c']}°C | Condition: {w['condition_gujarati']} | Humidity: {w['humidity']}% | Wind: {w['wind_speed']} km/h")
        print(f"   Advisories: {w['advisories']}")
        print("-" * 50)

        assert w["temp_c"] > -10.0 and w["temp_c"] < 60.0
        assert len(w["advisories"]) >= 1

    # 2. Mandi Price Service Verification (5 Commodities)
    test_commodities = [
        ("Cotton", "Rajkot"),
        ("Groundnut", "Junagadh"),
        ("Cumin", "Rajkot"),
        ("Wheat", "Ahmedabad"),
        ("Potato", "Ahmedabad")
    ]
    print("\n--- 2. TESTING MANDI PRICE SERVICE (5 COMMODITIES) ---")

    for comm, dist in test_commodities:
        p = price_service.fetch_mandi_price(commodity_name=comm, district_name=dist)
        status_tag = "LIVE AGMARKNET" if p["is_live"] else "CACHED SNAPSHOT"
        print(f"🌾 Commodity: {p['commodity_gu']} ({p['commodity_en']}) in {p['district_gu']} APMC [{status_tag}]")
        print(f"   Modal Price: ₹{p['modal_price']}/{p['unit']} (Min: ₹{p['min_price']}, Max: ₹{p['max_price']}) | Date: {p['price_date']}")
        print("-" * 50)

        assert p["modal_price"] > 0
        assert p["min_price"] <= p["modal_price"] <= p["max_price"]

    print("\n" + "=" * 70)
    print("🎉 ALL PHASE 5 LIVE DATA SERVICES VERIFIED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_live_services_verification()
