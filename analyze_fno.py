import pandas as pd
import os

# Find today's CSV files
latest_files = [f for f in os.listdir("data") if f.endswith(".csv")]
for file in latest_files:
    df = pd.read_csv(os.path.join("data", file))

    # Calculate total OI for Calls and Puts
    total_call_oi = df['CE_OI'].sum() if 'CE_OI' in df.columns else 0
    total_put_oi = df['PE_OI'].sum() if 'PE_OI' in df.columns else 0

    # Put/Call Ratio
    pcr = round(total_put_oi / total_call_oi, 2) if total_call_oi else "N/A"

    # Get top strike prices by volume
    if 'CE_TotVol' in df.columns:
        top_calls = df[['strikePrice', 'CE_TotVol']].sort_values(by='CE_TotVol', ascending=False).head(3)
        top_puts = df[['strikePrice', 'PE_TotVol']].sort_values(by='PE_TotVol', ascending=False).head(3)
    else:
        top_calls = top_puts = pd.DataFrame()

    print(f"\n📊 Report for: {file}")
    print(f"🟦 Total Call OI: {total_call_oi}")
    print(f"🟥 Total Put OI: {total_put_oi}")
    print(f"📈 PCR: {pcr}")
    print("🔥 Top Call Strikes:")
    print(top_calls)
    print("🔥 Top Put Strikes:")
    print(top_puts)
