import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_mutual_fund_data(scheme_code="120828"):
    """
    Fetches extended mutual fund data: 
    NAVs, Fund Rating, Risk Metrics, Expense Ratio, AUM, Dividend History
    """
    # --------------------------
    # Step 1: Fetch NAV & basic meta from MFAPI
    # --------------------------
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    res = requests.get(url).json()
    
    if "meta" not in res:
        return {"error": "Invalid scheme code or API error."}

    meta = res["meta"]
    navs = res["data"][:5]  # last 5 NAVs
    nav_df = pd.DataFrame(res["data"])
    
    fund_name = meta.get("scheme_name")
    fund_house = meta.get("fund_house")
    category = meta.get("scheme_category")
    
    # --------------------------
    # Step 2: Scrape Value Research for ratings/metrics
    # --------------------------
    try:
        vr_search_url = f"https://www.valueresearchonline.com/funds/{scheme_code}/mutual-fund-details"
        vr_res = requests.get(vr_search_url)
        soup = BeautifulSoup(vr_res.content, "html.parser")
        
        # Fund Rating (stars)
        rating_tag = soup.select_one(".rating-stars img")
        rating = rating_tag["alt"] if rating_tag else "N/A"
        
        # Risk Metrics
        risk_tag = soup.find("div", text="Riskometer")
        risk = risk_tag.find_next("div").text if risk_tag else "N/A"
        
        # Expense Ratio
        expense_tag = soup.find("div", text="Expense Ratio")
        expense_ratio = expense_tag.find_next("div").text if expense_tag else "N/A"
        
        # AUM
        aum_tag = soup.find("div", text="Assets Under Management")
        aum = aum_tag.find_next("div").text if aum_tag else "N/A"
        
        # Dividend Info
        dividend_tag = soup.find("div", text="Dividend History")
        dividend_info = dividend_tag.find_next("div").text if dividend_tag else "N/A"
        
    except Exception as e:
        rating = risk = expense_ratio = aum = dividend_info = "N/A"
        print("Value Research scrape failed:", e)
    
    return {
        "fund_name": fund_name,
        "fund_house": fund_house,
        "category": category,
        "navs": navs,
        "rating": rating,
        "risk": risk,
        "expense_ratio": expense_ratio,
        "aum": aum,
        "dividend_info": dividend_info,
        "nav_df": nav_df,  # full NAV history for charts
    }
