# src/05_financial_model.py
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
RETURN_COST_PCT = 0.05  # Japan COD return risk assumption
PRICE_COLS = ['our_new_price', 'our_price', 'price', 'base_price']

def evaluate_scenario(prices_csv, demand_csv):
    prices = pd.read_csv(os.path.join(DATA_DIR, prices_csv))
    demand = pd.read_csv(os.path.join(DATA_DIR, demand_csv))

    # Strip whitespace from columns
    prices.columns = prices.columns.str.strip()
    demand.columns = demand.columns.str.strip()

    # Rename sku columns if needed
    for df in [prices, demand]:
        if 'sku' in df.columns and 'sku_id' not in df.columns:
            df.rename(columns={'sku':'sku_id'}, inplace=True)

    # Merge with suffixes for overlapping columns
    df = demand.merge(prices, on=['sku_id','date'], how='left', suffixes=('_demand','_price'))

    # Determine price to use
    price_used = None
    for col in PRICE_COLS:
        if col+'_demand' in df.columns:
            price_used = df[col+'_demand']
            break
        if col+'_price' in df.columns:
            price_used = df[col+'_price']
            break
        if col in df.columns:
            price_used = df[col]
            break
    if price_used is None:
        raise KeyError(f"No price column found. Available: {list(df.columns)}")
    df['price_used'] = price_used

    # Determine units_sold
    for col in ['units_sold','demand']:
        if col+'_demand' in df.columns:
            df['units_sold'] = df[col+'_demand']
            break
        elif col+'_price' in df.columns:
            df['units_sold'] = df[col+'_price']
            break
        elif col in df.columns:
            df['units_sold'] = df[col]
            break
    else:
        df['units_sold'] = 0

    # Merge SKU costs
    skus = pd.read_csv(os.path.join(DATA_DIR,'skus.csv'))
    skus.columns = skus.columns.str.strip()
    if 'sku' in skus.columns and 'sku_id' not in skus.columns:
        skus.rename(columns={'sku':'sku_id'}, inplace=True)
    df = df.merge(skus[['sku_id','cost']], on='sku_id', how='left')

    # Compute financial metrics
    df['gmv'] = df['price_used'] * df['units_sold']
    df['gross_profit'] = (df['price_used'] - df['cost']) * df['units_sold']
    total_gmv = df['gmv'].sum()
    total_gross = df['gross_profit'].sum()
    return_cost = total_gmv * RETURN_COST_PCT
    net_profit = total_gross - return_cost

    return {
        'GMV': total_gmv,
        'GrossProfit': total_gross,
        'ReturnCost': return_cost,
        'NetProfit': net_profit,
        'rows': len(df)
    }

def compare(control_eval, test_eval):
    diff = {}
    for k in ['GMV','GrossProfit','ReturnCost','NetProfit']:
        diff[k+'_abs'] = test_eval[k] - control_eval[k]
        diff[k+'_pct'] = (test_eval[k] - control_eval[k]) / (control_eval[k] if control_eval[k] != 0 else 1)
    return diff

if __name__ == '__main__':
    ctl = evaluate_scenario('sales_sim.csv','sales_sim.csv')
    test = evaluate_scenario('prices_advanced.csv','sales_sim.csv')
    print("✅ Baseline:", ctl)
    print("✅ Test scenario:", test)
    print("📊 Difference:", compare(ctl,test))
