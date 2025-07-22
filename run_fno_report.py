import subprocess

# Run fetch script first
print("🔄 Fetching FnO data...")
subprocess.run(["python", "fetch_fno_data.py"])

# Then run analysis
print("🔍 Running analysis...")
subprocess.run(["python", "analyze_fno.py"])
