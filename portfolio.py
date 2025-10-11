from kite_api import get_live_quote

# User holdings
portfolio = {
    "RELIANCE": 5,
    "TCS": 2,
    "INFY": 3,
}

def get_portfolio_value():
    """
    Fetch live prices and compute portfolio value.
    Returns:
        df: list of dicts with stock info
        total_value: total portfolio value in ₹
    """
    data = {s: get_live_quote(s) for s in portfolio}
    df = []
    total_value = 0
    for stock, price in data.items():
        try:
            price = float(price)
        except:
            price = 0
        quantity = portfolio[stock]
        value = price * quantity
        df.append({
            "Stock": stock,
            "Live Price (₹)": price,
            "Quantity": quantity,
            "Value": value
        })
        total_value += value
    return df, total_value
