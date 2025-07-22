from nsepython import *
import pandas as pd
import datetime
import os

os.makedirs("data", exist_ok=True)
date_str = datetime.date.today().strftime("%Y-%m-%d")

def flatten(option_data):
    ce = option_data.get("CE", {})
    pe = option_data.get("PE", {})
    return {
        "strikePrice": option_data.get("strikePrice"),
        "expiryDate": option_data.get("expiryDate"),
        "CE_OI": ce.get("openInterest", 0),
        "PE_OI": pe.get("openInterest", 0),
        "CE_TotVol": ce.get("totalTradedVolume", 0),
        "PE_TotVol": pe.get("totalTradedVolume", 0)
    }

banknifty_raw = nse_optionchain_scrapper("BANKNIFTY")["records"]["data"]
nifty_raw = nse_optionchain_scrapper("NIFTY")["records"]["data"]

banknifty_flat = [flatten(row) for row in banknifty_raw]
nifty_flat = [flatten(row) for row in nifty_raw]

pd.DataFrame(banknifty_flat).to_csv(f"data/BANKNIFTY_{date_str}.csv", index=False)
pd.DataFrame(nifty_flat).to_csv(f"data/NIFTY_{date_str}.csv", index=False)

# Backup for trend comparison
pd.DataFrame(banknifty_flat).to_csv("data/BANKNIFTY_prev.csv", index=False)
pd.DataFrame(nifty_flat).to_csv("data/NIFTY_prev.csv", index=False)
