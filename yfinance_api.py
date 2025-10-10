import yfinance as yf

def get_historical_data(symbol="RELIANCE.NS", period="6mo"):
    stock = yf.Ticker(symbol)
    return stock.history(period=period)

def get_company_info(symbol="RELIANCE.NS"):
    stock = yf.Ticker(symbol)
    info = stock.info
    return {
        "Name": info.get("longName"),
        "Sector": info.get("sector"),
        "Market Cap": info.get("marketCap"),
        "P/E Ratio": info.get("trailingPE"),
        "52 Week High": info.get("fiftyTwoWeekHigh"),
        "52 Week Low": info.get("fiftyTwoWeekLow"),
    }
