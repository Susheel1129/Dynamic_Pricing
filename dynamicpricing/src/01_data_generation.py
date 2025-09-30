# src/01_data_generation.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

def generate_data(n_days=365, n_skus=100):
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_days)]
    
    categories = ["Beauty", "Electronics", "Apparel", "Lifestyle", "Home & Living"]
    seller_tiers = ["Standard", "Premium"]

    records = []
    for sku in range(n_skus):
        category = np.random.choice(categories)
        base_price = np.random.randint(1000, 10000)
        seller_tier = np.random.choice(seller_tiers)
        
        for date in dates:
            # Seasonality effect (Golden Week, Year-End sales)
            month = date.month
            if month in [4, 5]:   # Golden Week
                season_factor = 1.2
            elif month in [12]:   # Year-End
                season_factor = 1.5
            else:
                season_factor = 1.0

            # Demand ~ base price, category elasticity, season
            elasticity_map = {'Beauty': 1.8, 'Apparel': 1.5, 'Lifestyle': 1.3, 'Home & Living': 1.1, 'Electronics': 0.8}
            elasticity = elasticity_map[category]
            
            demand = int(np.random.poisson(lam=50 * season_factor / elasticity))
            
            records.append({
                "date": date,
                "sku": f"SKU_{sku}",
                "category": category,
                "seller_tier": seller_tier,
                "base_price": base_price,
                "demand": demand
            })
    
    return pd.DataFrame(records)

if __name__ == "__main__":
    df = generate_data()
    df.to_csv("../data/simulated_pricing_data.csv", index=False)
    print("✅ Simulated data saved to ../data/simulated_pricing_data.csv")
    print(df.head())
