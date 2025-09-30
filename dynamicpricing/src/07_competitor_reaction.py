import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def competitor_match(prices_csv, competitor_csv):
    prices = pd.read_csv(os.path.join(DATA_DIR, prices_csv))
    competitor = pd.read_csv(os.path.join(DATA_DIR, competitor_csv))

    # Merge prices with competitor data
    df = prices.merge(competitor, on=['sku_id', 'date'], how='left')

    # Identify our price and competitor price columns dynamically
    our_price_col = 'our_new_price' if 'our_new_price' in df.columns else 'our_price'
    
    # Find competitor price column
    competitor_price_cols = [c for c in df.columns if 'competitor' in c and 'price' in c]
    if len(competitor_price_cols) == 0:
        raise KeyError(f"No competitor price column found in {competitor_csv}. Columns: {list(df.columns)}")
    competitor_price_col = competitor_price_cols[0]  # pick first matching column

    # Initialize adjusted price
    df['adjusted_price'] = df[our_price_col]

    # Apply auto-match if our price > competitor_price * 1.05
    df.loc[df[our_price_col] > df[competitor_price_col] * 1.05, 'adjusted_price'] = df[competitor_price_col] * 1.05

    return df[['sku_id','date',our_price_col,competitor_price_col,'adjusted_price']]

if __name__ == "__main__":
    df = competitor_match('prices_advanced.csv','competitor_prices.csv')
    print(df.head())
    df.to_csv(os.path.join(DATA_DIR,'prices_adjusted.csv'), index=False)
    print(f"✅ Adjusted prices saved to {os.path.join(DATA_DIR,'prices_adjusted.csv')}")
