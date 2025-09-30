import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Load your advanced prices to get SKUs and dates
prices = pd.read_csv(os.path.join(DATA_DIR, 'prices_advanced.csv'))

# Simulate competitor prices as small random variation around our price
np.random.seed(42)
competitor_prices = prices[['sku_id', 'date']].copy()
competitor_prices['competitor_price'] = prices['our_new_price'] * (1 + np.random.uniform(-0.1, 0.1, size=len(prices)))

# Save to CSV
competitor_prices.to_csv(os.path.join(DATA_DIR, 'competitor_prices.csv'), index=False)
print(f"✅ competitor_prices.csv created with {len(competitor_prices)} rows in {DATA_DIR}")
