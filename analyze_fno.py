import pandas as pd
import os
from datetime import date

# Prepare report folder
os.makedirs("report", exist_ok=True)
today = date.today().strftime("%Y-%m-%d")
summary_lines = [f"# 📊 FnO Report for {today}\n"]

for file in os.listdir("data"):
    if file.endswith(".csv") and today in file:
        df = pd.read_csv(os.path.join("data", file))

        name = "BankNifty" if "BANKNIFTY" in file else "Nifty"
        ce_oi = df.get("CE_OI", pd.Series()).sum()
        pe_oi = df.get("PE_OI", pd.Series()).sum()
        pcr = round(pe_oi / ce_oi, 2) if ce_oi else "N/A"

        summary_lines.append(f"## 📘 {name}")
        summary_lines.append(f"- 🟦 Call OI: `{ce_oi}`")
        summary_lines.append(f"- 🔴 Put OI: `{pe_oi}`")
        summary_lines.append(f"- 🔄 PCR: `{pcr}`")

        if "CE_TotVol" in df.columns and "strikePrice" in df.columns:
            top_calls = df.sort_values("CE_TotVol", ascending=False).head(3)[["strikePrice", "CE_TotVol"]]
            top_puts = df.sort_values("PE_TotVol", ascending=False).head(3)[["strikePrice", "PE_TotVol"]]

            summary_lines.append("### 🔥 Top Call Strikes by Volume:")
            for _, row in top_calls.iterrows():
                summary_lines.append(f"- Strike: `{row['strikePrice']}` → Vol: `{row['CE_TotVol']}`")
            summary_lines.append("### 🔥 Top Put Strikes by Volume:")
            for _, row in top_puts.iterrows():
                summary_lines.append(f"- Strike: `{row['strikePrice']}` → Vol: `{row['PE_TotVol']}`")

# Save report
with open(f"report/fno_summary_{today}.md", "w") as f:
    f.write("\n".join(summary_lines))
