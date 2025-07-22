from nsepython import *
import pandas as pd
import datetime
import os

# Create folder for daily data
os.makedirs("data", exist_ok=True)

# Today's date for filenames
date_str = datetime.date.today().strftime("%Y-%m-%d")

def extract_flattened_rows(option_data):
    """Flatten each strike's CE/PE data for analysis."""
    strike = option_data.get("strikePrice")
    expiry = option_data.get("expiryDate")
    
    ce = option_data.get("CE", {})
    pe = option_data.get("PE", {})

    return {
        "strikePrice": strike,
        "expiryDate": expiry,
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
    """Scrape, flatten, and save option chain for a given index."""
    try:
        raw = nse_optionchain_scrapper(symbol)["records"]["data"]
        flat = [extract_flattened_rows(row) for row in raw]
        file_name = f"data/{symbol}_{date_str}.csv"
        pd.DataFrame(flat).to_csv(file_name, index=False)
        print(f"✅ Saved: {file_name}")
    except Exception as e:
        print(f"⚠️ Error fetching {symbol}: {e}")

# Fetch for NIFTY and BANKNIFTY
fetch_and_save("BANKNIFTY")
fetch_and_save("NIFTY")
