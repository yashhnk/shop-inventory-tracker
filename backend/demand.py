# demand.py
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import matplotlib.pyplot as plt

# ---------------------------
# Config
# ---------------------------
CSV_PATH = r"C:\Users\Aasavari\Downloads\SmartInventory_dm-main\backend\Grocery_Inventory_and_Sales_Dataset_Cleaned.csv"
RANDOM_SEED = 42

# ---------------------------
# Load dataset
# ---------------------------
df = pd.read_csv(CSV_PATH)

# Fix typo if present
if "Catagory" in df.columns:
    df = df.rename(columns={"Catagory": "Category"})

# ---------------------------
# Clean and preprocess
# ---------------------------
df["Unit_Price"] = (
    df["Unit_Price"].astype(str)
    .str.replace(r"[^0-9.]", "", regex=True)
    .replace("", "0")
    .astype(float)
)

for c in ["Date_Received", "Last_Order_Date", "Expiration_Date"]:
    if c in df.columns:
        df[c] = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
    else:
        df[c] = pd.NaT

if "Sales_Volume" not in df.columns:
    df["Sales_Volume"] = 0
else:
    df["Sales_Volume"] = pd.to_numeric(df["Sales_Volume"], errors="coerce").fillna(0)

# ---------------------------
# Derived features
# ---------------------------
df["Days_Since_Last_Order"] = (df["Date_Received"] - df["Last_Order_Date"]).dt.days.fillna(0).astype(int)
df["Days_Till_Expiry"] = (df["Expiration_Date"] - df["Date_Received"]).dt.days.fillna(0).astype(int)
df = df.sort_values(["Product_ID", "Date_Received"]).reset_index(drop=True)

df["Lag_1_Sales"] = df.groupby("Product_ID")["Sales_Volume"].shift(1).fillna(0)
df["Lag_7_Sales"] = df.groupby("Product_ID")["Sales_Volume"].shift(7).fillna(0)
df["Rolling_3_Sales"] = (
    df.groupby("Product_ID")["Sales_Volume"]
      .shift(1).rolling(3, min_periods=1).mean()
      .reset_index(level=0, drop=True).fillna(0)
)
df["Rolling_7_Sales"] = (
    df.groupby("Product_ID")["Sales_Volume"]
      .shift(1).rolling(7, min_periods=1).mean()
      .reset_index(level=0, drop=True).fillna(0)
)

df["Month"] = df["Date_Received"].dt.month.fillna(0).astype(int)
df["Weekday"] = df["Date_Received"].dt.weekday.fillna(0).astype(int)

df["Product_ID_Enc"] = df["Product_ID"].astype("category").cat.codes
df["Supplier_ID_Enc"] = df["Supplier_ID"].astype("category").cat.codes
df["Status_Enc"] = df["Status"].astype("category").cat.codes

df["Avg_Sales_Product"] = df.groupby("Product_ID")["Sales_Volume"].transform("mean").fillna(0)
df["Avg_Sales_Supplier"] = df.groupby("Supplier_ID")["Sales_Volume"].transform("mean").fillna(0)
df["Std_Sales_Product"] = df.groupby("Product_ID")["Sales_Volume"].transform("std").fillna(0)

# ---------------------------
# Train-test split
# ---------------------------
split_date = df["Date_Received"].quantile(0.8)
train_df = df[df["Date_Received"] <= split_date].copy()
test_df = df[df["Date_Received"] > split_date].copy()

# ---------------------------
# Features and Target
# ---------------------------
feature_cols = [
    "Stock_Quantity",
    "Reorder_Level",
    "Reorder_Quantity",
    "Unit_Price",
    "Days_Since_Last_Order",
    "Days_Till_Expiry",
    "Lag_1_Sales",
    "Lag_7_Sales",
    "Rolling_3_Sales",
    "Rolling_7_Sales",
    "Weekday",
    "Month",
    "Product_ID_Enc",
    "Supplier_ID_Enc",
    "Status_Enc",
    "Avg_Sales_Product",
    "Avg_Sales_Supplier",
    "Std_Sales_Product"
]

for c in feature_cols:
    if c not in df.columns:
        df[c] = 0
    if c not in train_df.columns:
        train_df[c] = 0
    if c not in test_df.columns:
        test_df[c] = 0

X_train = train_df[feature_cols].astype(float)
X_test = test_df[feature_cols].astype(float)

# Log-transform target
y_train = np.log1p(train_df["Sales_Volume"].astype(float))
y_test = np.log1p(test_df["Sales_Volume"].astype(float))

# ---------------------------
# Train XGBoost model
# ---------------------------
model = XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.9,
    colsample_bytree=0.9,
    random_state=RANDOM_SEED
)

model.fit(X_train, y_train)

# ---------------------------
# Evaluate
# ---------------------------
y_pred_log = model.predict(X_test)
y_pred = np.expm1(y_pred_log)
y_actual = np.expm1(y_test)

rmse = np.sqrt(mean_squared_error(y_actual, y_pred))
r2 = r2_score(y_actual, y_pred)

print(f"Test RMSE: {rmse:.4f}")
print(f"Test R²: {r2:.4f}")

# ---------------------------
# Correlation analysis
# ---------------------------
test_df["Predicted_Demand"] = y_pred
test_df["Actual_Demand"] = y_actual
corr_features = ["Predicted_Demand", "Actual_Demand", "Stock_Quantity", "Reorder_Level", "Reorder_Quantity", "Unit_Price"]

correlations = test_df[corr_features].corr(numeric_only=True)["Predicted_Demand"].sort_values(ascending=False)
print("\nTop correlated features with Predicted Demand:")
print(correlations)

# ---------------------------
# Save model
# ---------------------------
joblib.dump(model, "demandforecastingmodel.pkl")
print("\nSaved model -> demandforecastingmodel.pkl")

loaded = joblib.load("demandforecastingmodel.pkl")
print("Loaded model OK. Sample preds:", np.expm1(loaded.predict(X_test.iloc[:5])))

# Optional: Feature importance plot
plt.figure(figsize=(8,6))
plt.barh(X_train.columns, model.feature_importances_)
plt.title("XGBoost Feature Importance")
plt.tight_layout()
plt.show()
