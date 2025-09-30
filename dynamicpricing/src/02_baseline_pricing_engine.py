import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
OUT_DIR = DATA_DIR
CATEGORY_DISCOUNT = {'Beauty': 0.40, 'Electronics': 0.25, 'Apparel': 0.30, 'Lifestyle': 0.25, 'Home & Living': 0.25}
MARGIN_GUARDRAIL = 0.20   # minimum margin pct

def apply_discount(row):
    cap = CATEGORY_DISCOUNT.get(row['category'], 0.2)
    discount = cap
    new_price = row['base_price'] * (1 - discount)
    # ensure margin >= guardrail: margin_pct = (price - cost)/price
    cost = row['cost']
    margin_pct = (new_price - cost) / new_price if new_price > 0 else -1
    if margin_pct < MARGIN_GUARDRAIL:
        # set price to minimal price that gives guardrail
        new_price = cost / (1 - MARGIN_GUARDRAIL)
        discount = 1 - (new_price / row['base_price'])
    return round(new_price,2), round(discount,3)

def main():
    skus = pd.read_csv(os.path.join(DATA_DIR, 'skus.csv'))
    skus[['baseline_price','baseline_discount']] = skus.apply(lambda r: pd.Series(apply_discount(r)), axis=1)
    skus.to_csv(os.path.join(OUT_DIR, 'skus_baseline_prices.csv'), index=False)
    print("Baseline prices written to data/skus_baseline_prices.csv")

if __name__ == '__main__':
    main()
