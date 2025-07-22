import pandas as pd
import os
from datetime import date

today = date.today().strftime("%Y-%m-%d")
os.makedirs("report", exist_ok=True)

def format_number(n):
    try:
        return f"{int(n):,}"
    except:
        return str(n)

summary_lines = [f"# 📊 FnO Report for {today}\n"]

for file in os.listdir("data"):
    if file.endswith(".csv") and today in file:
        df = pd.read_csv(os.path.join("data", file))
        name = "BankNifty" if "BANKNIFTY" in file else "Nifty"

        ce_oi = df.get("CE_OI", pd.Series()).sum()
        pe_oi = df.get("PE_OI", pd.Series()).sum()
        pcr = round(pe_oi / ce_oi, 2) if ce_oi else "N/A"

        summary_lines.append(f"## 📘 {name}")
        summary_lines.append(f"- 🟦 Call OI: `{format_number(ce_oi)}`")
        summary_lines.append(f"- 🔴 Put OI: `{format_number(pe_oi)}`")
        summary_lines.append(f"- 🔄 PCR: `{pcr}`")

        # Trend comparison
        try:
            df_prev = pd.read_csv(f"data/{name.upper()}_prev.csv")
            prev_oi = df_prev.get("CE_OI", pd.Series()).sum()
            delta = ce_oi - prev_oi
            emoji = "📈" if delta > 0 else "📉"
            summary_lines.append(f"- 📊 CE OI Trend: `{format_number(delta)}` {emoji}")
        except:
            summary_lines.append("- ⚠️ No previous data to compare trend.")

        if "CE_TotVol" in df.columns and "strikePrice" in df.columns:
            top_calls = df.sort_values("CE_TotVol", ascending=False).head(3)[["strikePrice", "CE_TotVol"]]
            top_puts = df.sort_values("PE_TotVol", ascending=False).head(3)[["strikePrice", "PE_TotVol"]]

            summary_lines.append("### 🔥 Top Call Strikes by Volume:")
            for _, row in top_calls.iterrows():
                summary_lines.append(f"- Strike: `{row['strikePrice']}` → Vol: `{format_number(row['CE_TotVol'])}`")

            summary_lines.append("### 🔥 Top Put Strikes by Volume:")
            for _, row in top_puts.iterrows():
                summary_lines.append(f"- Strike: `{row['strikePrice']}` → Vol: `{format_number(row['PE_TotVol'])}`")

# Save markdown report
with open(f"report/fno_summary_{today}.md", "w") as f:
    f.write("\n".join(summary_lines))
