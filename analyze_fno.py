import pandas as pd
import os
from datetime import date, timedelta

# 📅 Prepare today's date
today = date.today()
today_str = today.strftime("%Y-%m-%d")

# 🗂 Get past 6 trading dates (skip weekends)
def get_recent_dates(n=6):
    dates = []
    check_day = today - timedelta(days=1)
    while len(dates) < n:
        if check_day.weekday() < 5:  # 0-4 = Mon-Fri
            dates.append(check_day.strftime("%Y-%m-%d"))
        check_day -= timedelta(days=1)
    return dates[::-1]  # oldest to newest

recent_dates = get_recent_dates()

# 📁 Ensure report folder exists
os.makedirs("report", exist_ok=True)

# 🔣 Format numbers with commas
def format_number(n):
    try:
        return f"{int(n):,}"
    except:
        return str(n)

summary_lines = [f"# 📊 FnO Report for {today_str}\n"]

for symbol in ["BANKNIFTY", "NIFTY"]:
    today_file = f"data/{symbol}_{today_str}.csv"
    if not os.path.exists(today_file):
        continue

    df_today = pd.read_csv(today_file)
    ce_oi = df_today.get("CE_OI", pd.Series()).sum()
    pe_oi = df_today.get("PE_OI", pd.Series()).sum()
    pcr = round(pe_oi / ce_oi, 2) if ce_oi else "N/A"

    summary_lines.append(f"## 📘 {symbol}")
    summary_lines.append(f"- 🟦 Call OI: `{format_number(ce_oi)}`")
    summary_lines.append(f"- 🔴 Put OI: `{format_number(pe_oi)}`")
    summary_lines.append(f"- 🔄 PCR: `{pcr}`")

    # 🔍 Trend Analysis for Top Strike
    top_col = "CE_TotVol" if pcr < 1 else "PE_TotVol"
    top_strike = df_today.sort_values(top_col, ascending=False).iloc[0]["strikePrice"]

    trend_data = []
    for d in recent_dates:
        path = f"data/{symbol}_{d}.csv"
        if os.path.exists(path):
            df = pd.read_csv(path)
            row = df[df["strikePrice"] == top_strike]
            if not row.empty:
                vol = row[top_col].values[0]
                oi_col = "CE_OI" if pcr < 1 else "PE_OI"
                oi = row[oi_col].values[0]
                ltp_col = "CE_LTP" if pcr < 1 else "PE_LTP"
                ltp = row[ltp_col].values[0]
                ident_col = "identifier_CE" if pcr < 1 else "identifier_PE"
                ident = row[ident_col].values[0]
                expiry = row["expiryDate"].values[0]
                trend_data.append({"date": d, "vol": vol, "oi": oi, "ltp": ltp, "identifier": ident, "expiry": expiry})

    # 📈 Analyze trend
    if len(trend_data) >= 3:
        vol_list = [v["vol"] for v in trend_data]
        oi_list = [v["oi"] for v in trend_data]

        vol_trend = "Increasing" if vol_list[-1] > vol_list[0] and vol_list[-2] > vol_list[1] else "Flat"
        oi_trend = "Increasing" if oi_list[-1] > oi_list[0] and oi_list[-2] > oi_list[1] else "Flat"

        summary_lines.append(f"- 📊 Strike `{top_strike}` Volume Trend: `{vol_trend}`")
        summary_lines.append(f"- 📊 Strike `{top_strike}` OI Trend: `{oi_trend}`")

        if vol_trend == "Increasing" and oi_trend == "Increasing":
            latest = trend_data[-1]
            ltp = latest["ltp"]
            entry = round(ltp, 2)
            target = round(entry * 1.5, 2)
            stop = round(entry * 0.7, 2)

            summary_lines.append(f"### 🧭 Trade Suggestion for {symbol}")
            summary_lines.append(f"- ✅ Direction: `{'Call' if pcr < 1 else 'Put'} Option`")
            summary_lines.append(f"- 🔢 Strike Price: `{top_strike}`")
            summary_lines.append(f"- 📆 Expiry: `{latest['expiry']}`")
            summary_lines.append(f"- 🎫 Option Symbol: `{latest['identifier']}`")
            summary_lines.append(f"- 💰 Entry (LTP): `{format_number(entry)}`")
            summary_lines.append(f"- 🎯 Target (+50%): `{format_number(target)}`")
            summary_lines.append(f"- ⛔ Stop-Loss (-30%): `{format_number(stop)}`")
        else:
            summary_lines.append(f"- ⚠️ No reliable signal for Strike `{top_strike}`. Skipping trade suggestion.")

# 📤 Save Report
with open(f"report/fno_summary_{today_str}.md", "w") as f:
    f.write("\n".join(summary_lines))
