from nsepython import *
import pandas as pd
import datetime
import os

# 📁 Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# 🗓️ Get today's date string
date_str = datetime.date.today().strftime("%Y-%m-%d")

def extract_flattened_rows(option_data):
    """Flatten CE and PE data for a strike."""
    ce = option_data.get("CE", {})
    pe = option_data.get("PE", {})

    return {
        "strikePrice": option_data.get("strikePrice"),
        "expiryDate": option_data.get("expiryDate"),

        "identifier_CE": ce.get("identifier", ""),
        "identifier_PE": pe.get("identifier", ""),

        "CE_OI": ce.get("openInterest", 0),
        "PE_OI": pe.get("openInterest", 0),

        "CE_TotVol": ce.get("totalTradedVolume", 0),
        "PE_TotVol": pe.get("totalTradedVolume", 0),

        "CE_LTP": ce.get("lastPrice", 0),
        "PE_LTP": pe.get("lastPrice", 0)
    }

def fetch_and_save(symbol):
    """Fetch option chain, flatten, and save as CSV."""
    try:
        raw_data = nse_optionchain_scrapper(symbol)["records"]["data"]
        flattened = [extract_flattened_rows(row) for row in raw_data]
        file_path = f"data/{symbol}_{date_str}.csv"
        pd.DataFrame(flattened).to_csv(file_path, index=False)
        print(f"✅ Saved: {file_path}")
    except Exception as e:
        print(f"⚠️ Failed to fetch {symbol}: {e}")

# ⛓️ Fetch and save for both indices
fetch_and_save("BANKNIFTY")
fetch_and_save("NIFTY")
