import sys
import json
import warnings
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score

# ==========================================
# PHASE 0: SETUP
# ==========================================
warnings.filterwarnings("ignore")
sys.stderr = open(os.devnull, 'w')

action = 'search'
args = sys.argv[1:]
if len(args) > 0: action = args[0]

# ==========================================
# PHASE 2: DATA LOADING
# ==========================================
csv_path = "/files_from_windows/November_Zillow_Dallas_11-16-22.csv"

try:
    # TRICK: Try to automatically detect the separator (, or ;)
    try:
        df = pd.read_csv(csv_path, sep=None, engine='python', on_bad_lines='skip')
    except:
        # Fallback
        df = pd.read_csv(csv_path, on_bad_lines='skip')

    # Clean column names (remove whitespace)
    df.columns = df.columns.str.strip()

    # CHECK: Do we have the correct columns?
    needed_cols = ['beds', 'baths', 'area', 'addressZipcode', 'unformattedPrice']
    
    # Sometimes price is just 'price'
    if 'price' in df.columns and 'unformattedPrice' not in df.columns:
        df.rename(columns={'price': 'unformattedPrice'}, inplace=True)

    missing = [c for c in needed_cols if c not in df.columns]
    if missing:
        # If we miss essential columns, we cannot proceed
        # We try to check if they might be named differently, otherwise error.
        all_cols = list(df.columns)
        raise ValueError(f"Missing columns: {missing}. Available: {all_cols}")

    # CONVERSION TO NUMBERS
    for c in needed_cols: 
        df[c] = pd.to_numeric(df[c], errors='coerce')
    
    # Drop rows without price or area
    df = df.dropna(subset=['unformattedPrice', 'area'])
    
    # IMPUTING (Fill empty values)
    imputer = SimpleImputer(strategy='median')
    df[['beds', 'baths']] = imputer.fit_transform(df[['beds', 'baths']])
    df['addressZipcode'] = df['addressZipcode'].fillna(0)
    
    X = df[['beds', 'baths', 'area', 'addressZipcode']]
    y = df['unformattedPrice']
    
    # PHASE 4: MODELING
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)

except Exception as e:
    print(json.dumps({"error": "Data Loading Error", "details": str(e)}))
    sys.exit()

# ==========================================
# PHASE 5: TOOLS
# ==========================================
result = {}

if action == 'predict':
    # TOOL: Valuation / Estimate Value
    try:
        if len(args) < 5:
            raise ValueError("Expects 4 parameters: beds baths area zip")
            
        p_beds = float(args[1])
        p_baths = float(args[2])
        p_area = float(args[3])
        p_zip = float(args[4])

        input_df = pd.DataFrame([[p_beds, p_baths, p_area, p_zip]], 
                                columns=['beds', 'baths', 'area', 'addressZipcode'])
        
        predicted = model.predict(input_df)[0]

        result = {
            "info": "Valuation",
            "input": {"beds": int(p_beds), "baths": int(p_baths), "sqft": int(p_area), "zip": int(p_zip)},
            "estimated_value": round(predicted, 2),
            "currency": "USD",
            "message": f"Estimate: ${int(predicted):,} for a house with {int(p_beds)} beds, {int(p_baths)} baths, {int(p_area)} sqft in {int(p_zip)}."
        }
    except Exception as e:
        result = {"error": "Calculation Error", "details": str(e)}

elif action == 'stats':
    preds = model.predict(X)
    r2 = r2_score(y, preds)
    result = {"info": "Stats", "R2": round(r2, 2)}

else: # SEARCH (Find deals)
    zip_filter = args[1] if len(args) > 1 else ''
    
    # 1. Predict
    df['AI_Price'] = model.predict(X)
    df['Pct'] = ((df['AI_Price'] - df['unformattedPrice']) / df['unformattedPrice']) * 100
    
    # 2. Filter (Only good deals)
    deals = df[(df['Pct'] > 5) & (df['Pct'] < 200)].copy()
    
    # 3. Zipcode filter
    if zip_filter:
        try: deals = deals[deals['addressZipcode'] == float(zip_filter)]
        except: pass
    
    # 4. Sort
    top = deals.sort_values('Pct', ascending=False).head(5)
    
    # 5. SELECT OUTPUT
    # We now explicitly add beds, baths and area to the output
    cols_out = ['address', 'unformattedPrice', 'AI_Price', 'Pct', 'detailUrl', 'beds', 'baths', 'area']
    
    # .fillna('') ensures that empty values do not cause a JSON error
    result = {
        "info": "Search", 
        "results": top[cols_out].fillna('').to_dict(orient='records')
    }

# Print result
print(json.dumps(result))