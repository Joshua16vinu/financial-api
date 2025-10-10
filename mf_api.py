import requests

def get_mutual_fund_data(scheme_code="120828"):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    res = requests.get(url).json()
    meta = res["meta"]
    navs = res["data"][:5]
    return {
        "fund_name": meta["scheme_name"],
        "fund_house": meta["fund_house"],
        "category": meta["scheme_category"],
        "navs": navs,
    }
