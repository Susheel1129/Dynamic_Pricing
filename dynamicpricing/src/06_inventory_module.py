# src/06_inventory_module.py
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def check_inventory(sales_csv, inventory_csv):
    sales = pd.read_csv(os.path.join(DATA_DIR,sales_csv))
    inventory = pd.read_csv(os.path.join(DATA_DIR,inventory_csv))

    # Strip whitespace
    sales.columns = sales.columns.str.strip()
    inventory.columns = inventory.columns.str.strip()

    # Rename SKU column
    for df in [sales, inventory]:
        if 'sku' in df.columns and 'sku_id' not in df.columns:
            df.rename(columns={'sku':'sku_id'}, inplace=True)

    # Determine units sold
    if 'units_sold' not in sales.columns:
        if 'demand' in sales.columns:
            sales['units_sold'] = sales['demand']
        else:
            sales['units_sold'] = 0

    df = sales.groupby('sku_id')['units_sold'].sum().reset_index()
    df = df.merge(inventory[['sku_id','inventory']], on='sku_id', how='left')
    df['shortfall'] = df['units_sold'] - df['inventory']
    df['shortfall'] = df['shortfall'].apply(lambda x: max(x,0))
    return df

if __name__ == '__main__':
    result = check_inventory('sales_sim.csv','inventory.csv')
    print(result.head())
