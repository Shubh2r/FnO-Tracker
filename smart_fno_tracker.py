import pandas as pd
import os
import datetime
import argparse
import yfinance as yf
from nsepython import nse_optionchain_scrapper

# 📁 Create folders
os.makedirs("data", exist_ok=True)
os.makedirs("report", exist_ok=True)

# 📅 Today and tomorrow
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
today_str = today.strftime("%Y-%m-%d")
tomorrow_str = tomorrow.strftime("%Y-%m-%d")

# 🗂 Configurable Mode
parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["evening", "morning"], default="evening")
args = parser.parse_args()
MODE = args.mode

# 📈 Global Index Tracker
def fetch_global_indices():
    indices = {
        "Dow": "^DJI",
        "Nasdaq": "^IXIC",
        "S&P 500": "^GSPC",
        "SGX Nifty": "^NSEI"
    }
    summary = {}
    for name, ticker in indices.items():
        try:
            data = yf.download(ticker, period="2d", interval="1d", progress=False)
            change = round(data["Close"].iloc[-1] - data["Close"].iloc[-2], 2)
            pct = round((change / data["Close"].iloc[-2]) * 100, 2)
            summary[name] = {"change": change, "percent": pct}
        except Exception as e:
            summary[name] = {"error": str(e)}
    return summary

# 📊 Fetch NSE FnO data
def extract_flattened_rows(option_data, spot):
    strike = option_data.get("strikePrice")
    expiry = option_data.get("expiryDate")

    ce = option_data.get("CE", {})
    pe = option_data.get("PE", {})

    if not ce.get("identifier") or not pe.get("identifier"):
        return None
    if ce.get("lastPrice", 0) == 0 and pe.get("lastPrice", 0) == 0:
        return None
    if abs(strike - spot) > 1500:
        return None

    try:
        exp_date = datetime.datetime.strptime(expiry, "%d-%b-%Y").date()
        if exp_date < today:
            return None
    except:
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

        date_save = tomorrow_str if MODE == "evening" else today_str
        pd.DataFrame(clean_rows).to_csv(f"data/{symbol}_{date_save}.csv", index=False)
        print(f"✅ Saved {len(clean_rows)} rows for {symbol} ({MODE})")
    except Exception as e:
        print(f"⚠️ Error fetching {symbol}: {e}")

# 🧠 Analyze and Recommend Trades
def analyze(symbol, global_data):
    filename = f"data/{symbol}_{tomorrow_str if MODE == 'evening' else today_str}.csv"
    if not os.path.exists(filename):
        return [f"⚠️ {symbol} data not available. Skipping..."]

    df = pd.read_csv(filename)
    ce_oi, pe_oi = df["CE_OI"].sum(), df["PE_OI"].sum()
    pcr = round(pe_oi / ce_oi, 2) if ce_oi else "N/A"
    top_col = "CE_TotVol" if pcr < 1 else "PE_TotVol"

    try:
        top_strike = df.sort_values(top_col, ascending=False).iloc[0]["strikePrice"]
    except:
        return [f"⚠️ No valid volume data for {symbol}."]

    row = df[df["strikePrice"] == top_strike].iloc[0]
    vol = row[top_col]
    oi = row["CE_OI"] if pcr < 1 else row["PE_OI"]
    ltp = row["CE_LTP"] if pcr < 1 else row["PE_LTP"]
    ident = row["identifier_CE"] if pcr < 1 else row["identifier_PE"]
    expiry = row["expiryDate"]

    entry = round(ltp, 2)
    target = round(entry * 1.5, 2)
    stop = round(entry * 0.7, 2)

    global_sentiment = sum([v["change"] for k, v in global_data.items() if isinstance(v, dict) and "change" in v])
    tag = "✅ Confirmed" if MODE == "morning" and global_sentiment > 0 else "⚠️ Global Risk" if global_sentiment < 0 else "🔍 Prelim"

    return [
        f"## 📘 {symbol} ({MODE.capitalize()} Mode)",
        f"- 📈 PCR: `{pcr}`",
        f"- 🔢 Top Strike: `{top_strike}`",
        f"- 📆 Expiry: `{expiry}`",
        f"- 🎫 Symbol: `{ident}`",
        f"- 💰 Entry: ₹{entry}",
        f"- 🎯 Target: ₹{target}",
        f"- ⛔ Stop-Loss: ₹{stop}",
        f"- 🌐 Global Sentiment: `{global_sentiment}`",
        f"### Trade Signal: {tag} ⇒ `{'Call' if pcr < 1 else 'Put'}` Option"
    ]

# 📝 Generate Final Report
def generate_report():
    global_data = fetch_global_indices()
    summary_lines = [f"# 📊 FnO Tracker Report – {tomorrow_str if MODE == 'evening' else today_str}"]
    
    for name, vals in global_data.items():
        if "error" in vals:
            summary_lines.append(f"- ⚠️ {name}: `{vals['error']}`")
        else:
            summary_lines.append(f"- 🌐 {name}: Change `{vals['change']}` ({vals['percent']}%)")

    for symbol in ["BANKNIFTY", "NIFTY"]:
        summary_lines += analyze(symbol, global_data)

    file_name = f"report/fno_{MODE}_report_{tomorrow_str if MODE == 'evening' else today_str}.md"
    with open(file_name, "w") as f:
        f.write("\n".join(summary_lines))
    print(f"📝 Report saved as {file_name}")

# 🚦 Execution Flow
fetch_and_save("BANKNIFTY")
fetch_and_save("NIFTY")
generate_report()
