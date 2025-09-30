import pandas as pd
import os
from math import isclose

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
OUT_DIR = DATA_DIR

AUTO_MATCH_THRESHOLD = 0.05   # if our price is > competitor * (1 + 0.05)
AUTO_MATCH_TARGET_ABOVE = 0.02  # we match at competitor*(1+0.02)
MARGIN_GUARDRAIL = 0.20
CATEGORY_DISCOUNT_CAP = {'Beauty': 0.40, 'Electronics': 0.25, 'Apparel': 0.30, 'Lifestyle': 0.25, 'Home & Living': 0.25}
LUXURY_MAX_DISCOUNT = 0.30

def compute_new_price(sku_row, competitor_price):
    base_price = sku_row['base_price']
    cost = sku_row['cost']
    cat = sku_row['category']
    is_lux = sku_row.get('is_luxury', False)

    cap = CATEGORY_DISCOUNT_CAP.get(cat, 0.2)
    if is_lux:
        cap = min(cap, LUXURY_MAX_DISCOUNT)

    # baseline attempt
    target_price = base_price * (1 - cap)

    # auto-match logic
    if target_price > competitor_price * (1 + AUTO_MATCH_THRESHOLD):
        # match close to competitor but keep tiny buffer
        attempted_price = competitor_price * (1 + AUTO_MATCH_TARGET_ABOVE)
        target_price = min(attempted_price, target_price)

    # Ensure margin guardrail: if price too low, lift price
    if target_price <= cost:
        target_price = cost * (1 + MARGIN_GUARDRAIL)  # ensure at least guardrail
    else:
        margin_pct = (target_price - cost) / target_price
        if margin_pct < MARGIN_GUARDRAIL:
            # compute minimum price for guardrail
            min_price_for_guardrail = cost / (1 - MARGIN_GUARDRAIL)
            target_price = max(target_price, min_price_for_guardrail)

    discount = 1 - (target_price / base_price)
    return round(target_price,2), round(discount,4)

def main():
    skus = pd.read_csv(os.path.join(DATA_DIR, 'skus.csv')).set_index('sku_id')
    sales = pd.read_csv(os.path.join(DATA_DIR, 'sales_sim.csv'))
    # Keep unique competitor price per sku/date for simplicity - use mean if multiples
    comp = sales.groupby(['sku_id','date'])['competitor_price'].mean().reset_index()

    out_rows = []
    for _, row in comp.iterrows():
        sku_id = row['sku_id']
        comp_price = row['competitor_price']
        sku_row = skus.loc[sku_id]
        new_price, discount = compute_new_price(sku_row, comp_price)
        out_rows.append({'sku_id':sku_id, 'date':row['date'], 'competitor_price':comp_price,
                         'our_new_price':new_price, 'discount':discount})
    out_df = pd.DataFrame(out_rows)
    out_df.to_csv(os.path.join(OUT_DIR, 'prices_advanced.csv'), index=False)
    print("Advanced prices saved to data/prices_advanced.csv")

if __name__ == '__main__':
    main()
