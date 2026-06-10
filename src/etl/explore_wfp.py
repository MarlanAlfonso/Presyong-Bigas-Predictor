import pandas as pd

RAW_PATH = "data/raw/wfp_philippines_food_prices.csv"
OUT_PATH = "data/processed/wfp_philippines_food_prices.csv"

df = pd.read_csv(RAW_PATH)

# Audit: see all unique comodity and region names
print ("=== Commodities ===")
print (df['commodity'].unique())

print ("=== Regions (admin1 )===")
print (df['admin1'].unique())

print("\n=== Price types ===")
print(df["pricetype"].unique())

print(f"\nTotal rows: {len(df)}")
print(f"Date range: {df['date'].min()} → {df['date'].max()}")

# Filter 
ncr_rice = df[ 
    (df["commodity"].str.contains("Rice", case=False, na=False)) &
    (df["admin1"].str.contains("National Capital Region", case=False, na=False)) &
    (df["pricetype"] == "Retail")
].copy()

# Parse date and sort 
ncr_rice["date"] = pd.to_datetime(ncr_rice["date"])
ncr_rice = ncr_rice.sort_values("date").reset_index(drop=True)

# Audit the result 
print(f"\nFiltered rows: {len(ncr_rice)}")
print(f"Date range: {ncr_rice['date'].min()} → {ncr_rice['date'].max()}")
print(ncr_rice[["date", "market", "commodity", "price", "currency"]].head(10))

# Save the filtered data
ncr_rice.to_csv(OUT_PATH, index=False)
print(f"\nSaved to: {OUT_PATH}")