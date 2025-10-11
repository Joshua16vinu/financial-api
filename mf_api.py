import requests
import pandas as pd

def get_mutual_fund_data(scheme_code="120828"):
    """Fetch mutual fund info and NAV data from mfapi.in with graceful fallbacks."""
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        res = requests.get(url).json()

        if "meta" not in res or "data" not in res:
            return {"error": "Invalid or missing mutual fund data."}

        meta = res["meta"]
        navs = res["data"][:30]  # last 30 NAVs

        nav_df = pd.DataFrame(navs)
        nav_df["date"] = pd.to_datetime(nav_df["date"], format="%d-%m-%Y", errors="coerce")
        nav_df["nav"] = pd.to_numeric(nav_df["nav"], errors="coerce")

        # Return all fields (safe even if missing)
        return {
            "fund_name": meta.get("scheme_name", "Unknown Fund"),
            "fund_house": meta.get("fund_house", "Unknown AMC"),
            "category": meta.get("scheme_category", "N/A"),
            "rating": meta.get("rating", "N/A"),
            "risk": meta.get("riskometer", "N/A"),
            "expense_ratio": meta.get("expense_ratio", "N/A"),
            "aum": meta.get("aum", "N/A"),
            "dividend_info": meta.get("dividend_type", "N/A"),
            "nav_df": nav_df
        }

    except Exception as e:
        return {"error": f"Failed to fetch mutual fund data: {str(e)}"}
