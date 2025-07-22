from nsepython import nse_optionchain_scrapper, nse_fno_lot_info
import pandas as pd
import datetime
import os

# 📁 Create data folder
os.makedirs("data", exist_ok=True)

# 🗓️ Get today's date
today = datetime.date.today()
date_str = today.strftime("%Y-%m-%d")

def extract_flattened_rows(option_data, spot, symbol):
    strike = option_data.get("strikePrice")
    expiry = option_data.get("expiryDate")

    # 🎯 Only include strikes within ±1500 of spot
    if abs(strike - spot) > 1500:
        return None

    ce = option_data.get("CE", {})
    pe = option_data.get("PE", {})

    # 🧹 Drop rows with missing identifiers or premiums
    if not ce.get("identifier") or not pe.get("identifier"):
        return None
    if ce.get("lastPrice", 0) == 0 and pe.get("lastPrice", 0) == 0:
        return None

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
    try:
        spot_price = nse_fno_lot_info(symbol)["spot_price"]
        raw_data = nse_optionchain_scrapper(symbol)["records"]["data"]
        rows = [
            extract_flattened_rows(row, spot_price, symbol)
            for row in raw_data
        ]
        clean_rows = [r for r in rows if r is not None]
        pd.DataFrame(clean_rows).to_csv(f"data/{symbol}_{date_str}.csv", index=False)
        print(f"✅ Fetched & saved {symbol} data with {len(clean_rows)} clean rows.")
    except Exception as e:
        print(f"⚠️ Error fetching {symbol}: {e}")

fetch_and_save("BANKNIFTY")
fetch_and_save("NIFTY")
