import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Load your simulated SKUs
sales = pd.read_csv(os.path.join(DATA_DIR, 'sales_sim.csv'))

# Get unique SKUs
skus = sales['sku_id'].unique()

# Generate random inventory between 500 and 2000 units per SKU
import numpy as np
inventory = pd.DataFrame({
    'sku_id': skus,
    'inventory': np.random.randint(500, 2000, size=len(skus))
})

# Save inventory.csv
inventory.to_csv(os.path.join(DATA_DIR, 'inventory.csv'), index=False)
print(f"✅ inventory.csv created with {len(skus)} SKUs in {DATA_DIR}")
