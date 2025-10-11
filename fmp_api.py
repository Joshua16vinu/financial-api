import requests
import pandas as pd

def get_mutual_fund_data(scheme_code="120828"):
    """Fetch mutual fund data using mfapi.in and enrich with Value Research (if available)."""
    try:
        # --- Base data from mfapi.in ---
        mf_url = f"https://api.mfapi.in/mf/{scheme_code}"
        res = requests.get(mf_url).json()

        if "meta" not in res or "data" not in res:
            return {"error": "Invalid or missing mutual fund data."}

        meta = res["meta"]
        navs = res["data"][:30]
        nav_df = pd.DataFrame(navs)
        nav_df["date"] = pd.to_datetime(nav_df["date"], format="%d-%m-%Y", errors="coerce")
        nav_df["nav"] = pd.to_numeric(nav_df["nav"], errors="coerce")

        # --- Optional enrichment from Value Research ---
        enrichment = {}
        try:
            vr_url = f"https://api.valueresearchonline.com/funds/fund-performance?code={scheme_code}"
            val = requests.get(vr_url, timeout=3).json()
            if val:
                enrichment = {
                    "rating": val.get("rating", "N/A"),
                    "risk": val.get("riskometer", "N/A"),
                    "aum": val.get("aum", "N/A"),
                    "expense_ratio": val.get("expenseRatio", "N/A"),
                }
        except Exception:
            enrichment = {
                "rating": "N/A",
                "risk": "N/A",
                "aum": "N/A",
                "expense_ratio": "N/A",
            }

        # Combine both
        return {
            "fund_name": meta.get("scheme_name", "Unknown Fund"),
            "fund_house": meta.get("fund_house", "Unknown AMC"),
            "category": meta.get("scheme_category", "N/A"),
            "dividend_info": meta.get("dividend_type", "N/A"),
            "nav_df": nav_df,
            **enrichment,
        }

    except Exception as e:
        return {"error": f"Failed to fetch mutual fund data: {str(e)}"}
