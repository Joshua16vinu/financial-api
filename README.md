# Smart Financial API Usage Dashboard

---

## **Objective**

Build an AI-powered financial dashboard that provides insights for **stocks and mutual funds**, including live prices, historical data, portfolio valuation, mutual fund metrics, and AI-driven recommendations.

---

## **1️⃣ Features**

### Stock Data

- Fetch live prices (Kite API)
- Fetch company profile (FMP API)
- Plot historical price trends (last 6 months)
- Display fundamental metrics: P/E ratio, 52-week high/low, dividend yield, beta, market cap

### Mutual Funds

- Fetch NAVs (MFAPI)
- Extended metrics from Value Research:
    - Fund rating//premium
    - Risk//premium
    - Expense ratio//premium
    - AUM//premium
    - Dividend history//premium
- NAV charts

### Portfolio Management

- Combine stocks and mutual funds
- Calculate live portfolio value
- Show gain/loss percentages
- AI-driven rebalancing suggestions

### AI Insights

- GPT-4 provides portfolio insights
- Suggest top gainers/losers
- Personalized investment advice
- Chat interface for portfolio queries

---

## **2️⃣ APIs Used**

### Stocks

- **Kite Connect**: live quotes, trades (requires Connect plan)
- **yFinance**: fallback for historical & live prices
- **FMP API**: company profile, historical OHLC data, fundamentals

### Mutual Funds

- **MFAPI**: NAVs & basic meta
- **Value Research**: ratings, risk metrics, expense ratio, AUM, dividend info

### AI

- **OpenAI GPT-4**: portfolio insights, chat assistant

---

## **3️⃣ FMP API Parameters**

**Company Profile Endpoint:** `/profile/{symbol}`

- `companyName`
- `industry`
- `sector`
- `mktCap`
- `priceEarningsRatio`
- `range52WeekHigh`
- `range52WeekLow`
- `dividendYield`
- `beta`
- `volAvg`
- `lastDiv`

**Historical Prices Endpoint:** `/historical-price-full/{symbol}`

- `date`
- `open`, `high`, `low`, `close`
- `adjClose`
- `volume`
- `unadjustedVolume`
- `change`, `changePercent`, `vwap`

---

## **4️⃣ fmp_api.py**

```python
import requests
import pandas as pd
import streamlit as st

FMP_API_KEY = st.secrets.get("fmp_api_key", "YOUR_FMP_KEY")
BASE_URL = "https://financialmodelingprep.com/api/v3"

# --- Historical Stock Data ---
def get_historical_data(symbol="RELIANCE", period="6mo"):
    url = f"{BASE_URL}/historical-price-full/{symbol}?apikey={FMP_API_KEY}"
    res = requests.get(url).json()
    if "historical" in res:
        df = pd.DataFrame(res["historical"])
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").set_index("date")
        last_6mo = df.last('6M')
        return last_6mo
    return pd.DataFrame()

# --- Company Profile ---
def get_company_info(symbol="RELIANCE"):
    url = f"{BASE_URL}/profile/{symbol}?apikey={FMP_API_KEY}"
    res = requests.get(url).json()
    if res:
        info = res[0]
        return {k: (v if v is not None else 'Data unavailable') for k, v in {
            "Name": info.get("companyName"),
            "Industry": info.get("industry"),
            "Sector": info.get("sector"),
            "Market Cap": info.get("mktCap"),
            "P/E Ratio": info.get("priceEarningsRatio"),
            "52 Week High": info.get("range52WeekHigh"),
            "52 Week Low": info.get("range52WeekLow"),
            "Dividend Yield": info.get("dividendYield"),
            "Beta": info.get("beta"),
            "Average Volume": info.get("volAvg"),
            "Last Dividend": info.get("lastDiv"),
        }.items()}
    return {}

```

---

## **5️⃣ mf_api.py**

```python
import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_mutual_fund_data(scheme_code="120828"):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    res = requests.get(url).json()
    if "meta" not in res:
        return {"error": "Invalid scheme code or API error."}

    meta = res["meta"]
    navs = res["data"][:5]
    nav_df = pd.DataFrame(res["data"])

    # Basic info
    fund_name = meta.get("scheme_name")
    fund_house = meta.get("fund_house")
    category = meta.get("scheme_category")

    # Scrape Value Research
    try:
        vr_url = f"https://www.valueresearchonline.com/funds/{scheme_code}/mutual-fund-details"
        soup = BeautifulSoup(requests.get(vr_url).content, "html.parser")
        rating_tag = soup.select_one(".rating-stars img")
        rating = rating_tag["alt"] if rating_tag else "N/A"
        risk_tag = soup.find("div", text="Riskometer")
        risk = risk_tag.find_next("div").text if risk_tag else "N/A"
        expense_tag = soup.find("div", text="Expense Ratio")
        expense_ratio = expense_tag.find_next("div").text if expense_tag else "N/A"
        aum_tag = soup.find("div", text="Assets Under Management")
        aum = aum_tag.find_next("div").text if aum_tag else "N/A"
        dividend_tag = soup.find("div", text="Dividend History")
        dividend_info = dividend_tag.find_next("div").text if dividend_tag else "N/A"
    except:
        rating = risk = expense_ratio = aum = dividend_info = "N/A"

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
        "nav_df": nav_df,
    }

```

---

## **6️⃣ main.py Integration Notes**

- Use FMP API for stock info and historical data
- Use MFAPI + Value Research for mutual funds
- Parse NAV dates with `dayfirst=True`
- Sort NAVs by date before plotting
- Handle missing fields gracefully
- AI insights can incorporate risk, rating, expense ratio, and P/E ratio

```python
# Example for NAV date parsing
nav_df["date"] = pd.to_datetime(nav_df["date"], dayfirst=True)
nav_df = nav_df.sort_values("date")
st.line_chart(nav_df.set_index("date")["nav"])

```

---

## **7️⃣ Running**

```bash
pip install -r requirements.txt
streamlit run main.py

```

---

## **>>Kite Connect – Key Handling & Limitations**

### Generating Keys & Tokens

1. **API Key & Secret**: Create an app on Kite Connect (requires Connect plan) → get `api_key` and `api_secret`.
2. **Login URL**: Use `kite.login_url()` to generate a login link for user authentication.
3. **Request Token**: After login, Kite redirects to your redirect URL with `request_token`.
4. **Access Token**: Exchange the `request_token` using `kite.generate_session(request_token, api_secret=API_SECRET)` → returns `access_token`.
5. **Set Access Token**: `kite.set_access_token(access_token)` to authorize API calls.

### Feasibility Note

- **Free version limitation**: Users cannot fetch live quotes or historical data via Kite API without the Connect plan.
- **Request token input**: Users need to paste a new request token each time to generate a fresh access token; this is **not practical for daily use**.
- Recommendation: Use a paid Kite Connect app for seamless access or fallback to FMP/yFinance for demonstration.

![WhatsApp Image 2025-10-11 at 00.34.39_1eaa2879.jpg](attachment:6abb34e3-fa2a-44e7-bcc0-1ff0cc87d57f:WhatsApp_Image_2025-10-11_at_00.34.39_1eaa2879.jpg)

## IS PASTING REQUEST TOKEN FEASIBLE FROM USER POV?

### **1️⃣ Why pasting request token every time is needed**

- Kite Connect **access tokens expire in a single session**.
- Request token is a **one-time temporary code** returned after logging in via the Kite login URL.
- So yes, for the free/demo flow without storing tokens, the user must manually paste it each session.
- ✅ Technically feasible, but **not practical for a real app**, especially for frequent use.

---

