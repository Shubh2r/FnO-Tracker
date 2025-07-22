from nsepython import *
import pandas as pd
import datetime
import os

# Create data folder if it doesn't exist
os.makedirs("data", exist_ok=True)

# Today's date for filename
date_str = datetime.date.today().strftime("%Y-%m-%d")

def extract_flattened_rows(option_data):
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
    try:
        raw = nse_optionchain_scrapper(symbol)["records"]["data"]
        flattened = [extract_flattened_rows(row) for row in raw]
        pd.DataFrame(flattened).to_csv(f"data/{symbol}_{date_str}.csv", index=False)
        print(f"✅ Saved {symbol} data as {symbol}_{date_str}.csv")
    except Exception as e:
        print(f"⚠️ Error fetching {symbol}: {e}")

# Fetch and save both indices
fetch_and_save("BANKNIFTY")
fetch_and_save("NIFTY")
