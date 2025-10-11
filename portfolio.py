from kite_api import get_live_quote

portfolio = {
    "RELIANCE": 5,
    "TCS": 2,
    "INFY": 3,
}

def get_portfolio_value(portfolio_dict):
    data = {s: get_live_quote(s) for s in portfolio_dict}
    df = []
    total_value = 0
    for stock, price in data.items():
        try:
            price = float(price)  # convert to float
        except:
            price = 0  # fallback if quote failed
        quantity = portfolio_dict[stock]
        value = price * quantity
        df.append({
            "Stock": stock,
            "Live Price (₹)": price,
            "Quantity": quantity,
            "Value": value
        })
        total_value += value
    return df, total_value
