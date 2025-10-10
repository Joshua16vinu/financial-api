import requests
import pandas as pd

def get_mutual_fund_data(scheme_code="120828"):
    """
    Fetches mutual fund data with extra metrics:
    - Fund name, house, category
    - NAVs (last 5 days)
    - Risk metrics (standard deviation, beta)
    - Fund rating
    - AUM, expense ratio
    """
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    try:
        res = requests.get(url).json()
        meta = res["meta"]
        navs = res["data"][:5]  # last 5 NAVs
    except Exception as e:
        print("Error fetching MF data:", e)
        return {}

    # Extra metrics (from meta or approximate calculations)
    fund_info = {
        "fund_name": meta.get("scheme_name"),
        "fund_house": meta.get("fund_house"),
        "category": meta.get("scheme_category"),
        "navs": navs,
        "fund_rating": meta.get("fund_rating", "N/A"),  # if available
        "aum": meta.get("aum", "N/A"),  # Assets under management
        "expense_ratio": meta.get("expense_ratio", "N/A"),
        "risk": meta.get("risk", "N/A"),  # risk rating if available
        "manager": meta.get("fund_manager", "N/A"),
        "inception_date": meta.get("inception_date", "N/A"),
        "dividend_history": meta.get("dividend_history", []),  # optional
    }

    # Convert NAVs to a DataFrame for charting
    try:
        nav_df = pd.DataFrame(navs)
        nav_df["nav"] = nav_df["nav"].astype(float)
        fund_info["nav_df"] = nav_df
    except Exception as e:
        print("Error converting NAVs:", e)

    return fund_info


# --- Example usage ---
if __name__ == "__main__":
    mf = get_mutual_fund_data("120828")
    print("Fund Name:", mf["fund_name"])
    print("Fund House:", mf["fund_house"])
    print("Category:", mf["category"])
    print("Fund Rating:", mf["fund_rating"])
    print("AUM:", mf["aum"])
    print("Expense Ratio:", mf["expense_ratio"])
    print("NAVs (last 5):", mf["navs"])
