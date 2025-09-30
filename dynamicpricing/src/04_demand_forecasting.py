# src/04_demand_forecasting.py
import os
import pandas as pd
import lightgbm as lgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

DATA_PATH = "../data/simulated_pricing_data.csv"
MODEL_DIR = "../models"
MODEL_PATH = os.path.join(MODEL_DIR, "demand_forecast.pkl")

def prepare_features():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df['dayofweek'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month

    # One-hot encode only if the columns exist
    categorical_cols = [c for c in ['category', 'seller_tier'] if c in df.columns]
    if categorical_cols:
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    # Drop non-feature cols if present and build X,y
    drop_cols = [c for c in ['date', 'sku'] if c in df.columns]
    X = df.drop(columns=drop_cols + ['demand'], errors='ignore')
    # Remove whitespace in feature names (LightGBM warning avoidance)
    X.columns = X.columns.str.replace(' ', '_')
    y = df['demand']
    return X, y

def train():
    os.makedirs(MODEL_DIR, exist_ok=True)
    X, y = prepare_features()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = lgb.LGBMRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=6,
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    # Regression metrics
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"✅ Model trained.")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    print(f"R² Score: {r2:.4f}")

    joblib.dump(model, MODEL_PATH)
    print(f"📦 Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()
