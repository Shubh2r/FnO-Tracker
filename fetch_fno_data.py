from nsepython import *
import pandas as pd
import datetime
import os  # ✅ Add this to create folders

# Create the folder safely
os.makedirs("data", exist_ok=True)

date_str = datetime.date.today().strftime("%Y-%m-%d")

banknifty = nse_optionchain_scrapper("BANKNIFTY")
nifty = nse_optionchain_scrapper("NIFTY")

# Save to CSVs
pd.DataFrame(banknifty["records"]["data"]).to_csv(f"data/BANKNIFTY_{date_str}.csv", index=False)
pd.DataFrame(nifty["records"]["data"]).to_csv(f"data/NIFTY_{date_str}.csv", index=False)
