import pandas as pd
import os
from datetime import date, timedelta

today = date.today()
today_str = today.strftime("%Y-%m-%d")
os.makedirs("report", exist_ok=True)

def format_number(n):
    try:
        return f"{int(n):,}"
    except:
        return str(n)

def get_previous_trading_day(today):
    previous_day = today - timedelta(days=1)
    while previous_day.weekday() > 4:  # 5 = Saturday, 6 = Sunday
        previous_day -= timedelta(days=1)
    return previous_day.strftime("%Y-%m-%d")

yesterday_str = get_previous_trading_day(today)

summary_lines = [f"# 📊 FnO Report for {today_str}\n"]

for file in os.listdir("data"):
    if file.endswith(".csv") and today_str in file:
        df = pd.read_csv(os.path.join("data", file))
        name = "BankNifty" if "BANKNIFTY" in file else "Nifty"

        ce_oi = df.get("CE_OI", pd.Series()).sum()
        pe_oi = df.get("PE_OI", pd.Series()).sum()
        pcr = round(pe_oi / ce_oi, 2) if ce_oi else "N/A"

        summary_lines.append(f"## 📘 {name}")
        summary_lines.append(f"- 🟦 Call OI: `{format_number(ce_oi)}`")
        summary_lines.append(f"- 🔴 Put OI: `{format_number(pe_oi)}`")
        summary_lines.append(f"- 🔄 PCR: `{pcr}`")

        # 🔁 Compare with previous trading day
        yesterday_file = f"data/{name.upper()}_{yesterday_str}.csv"
        if os.path.exists(yesterday_file):
            prev_df = pd.read_csv(yesterday_file)
            prev_oi = prev_df.get("CE_OI", pd.Series()).sum()
            delta = ce_oi - prev_oi
            emoji = "📈" if delta > 0 else "📉" if delta < 0 else "➖"
            summary_lines.append(f"- 📊 CE OI Change since {yesterday_str}: `{format_number(delta)}` {emoji}")
        else:
            summary_lines.append(f"- ⚠️ No previous file for {yesterday_str} to compare.")

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
with open(f"report/fno_summary_{today_str}.md", "w") as f:
    f.write("\n".join(summary_lines))
