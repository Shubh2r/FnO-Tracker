from nsepython import nse_optionchain_scrapper
import pandas as pd
import datetime
import os

# 📁 Create data folder
os.makedirs("data", exist_ok=True)

# 🗓️ Today's date string
date_str = datetime.date.today().strftime("%Y-%m-%d")

def extract_flattened_rows(option_data, spot):
    strike = option_data.get("strikePrice")
    expiry = option_data.get("expiryDate")

    # 🎯 Keep only strikes near spot
    if abs(strike - spot) > 1500:
        return None

    ce = option_data.get("CE", {})
    pe = option_data.get("PE", {})

    # 🧹 Skip rows with missing symbols or zero premiums
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
        chain = nse_optionchain_scrapper(symbol)
        spot = float(chain["records"]["underlyingValue"])
        raw = chain["records"]["data"]

        rows = [extract_flattened_rows(row, spot) for row in raw]
        clean_rows = [r for r in rows if r]

        pd.DataFrame(clean_rows).to_csv(f"data/{symbol}_{date_str}.csv", index=False)
        print(f"✅ Saved {len(clean_rows)} clean rows for {symbol}")
    except Exception as e:
        print(f"⚠️ Error fetching {symbol}: {e}")

# 🚀 Fetch for both indices
fetch_and_save("BANKNIFTY")
fetch_and_save("NIFTY")
