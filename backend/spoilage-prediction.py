import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# --- Step 1: Load the cleaned dataset ---
df = pd.read_csv(r"C:\Users\Aasavari\Downloads\SmartInventory_dm-main\backend\Grocery_Inventory_and_Sales_Dataset_Cleaned.csv")

# --- Step 2: Convert date columns properly ---
date_cols = ['Date_Received', 'Last_Order_Date', 'Expiration_Date']
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# --- Step 3: Derive useful features ---
df['DaysRemaining'] = (df['Expiration_Date'] - pd.Timestamp.today()).dt.days
df['DaysRemaining'] = df['DaysRemaining'].fillna(0)

# Avoid divide by zero for AvgDailySales
df['AvgDailySales'] = np.where(
    df['DaysRemaining'] > 0,
    df['Sales_Volume'] / df['DaysRemaining'],
    0
)

# --- Step 4: Create target column ---
df['WillExpire'] = np.where(
    (df['Stock_Quantity'] > df['Sales_Volume']) & (df['DaysRemaining'] <= 0),
    1, 0
)

# --- Step 5: Select features and target ---
features = [
    'Stock_Quantity', 'Reorder_Level', 'Reorder_Quantity',
    'Unit_Price', 'Sales_Volume', 'DaysRemaining', 'AvgDailySales'
]
target = 'WillExpire'

X = df[features]
y = df[target]

# --- Step 6: Train-test split ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# --- Step 7: Train RandomForest model ---
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# --- Step 8: Evaluate model ---
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# --- Step 9: Confusion Matrix ---
plt.figure(figsize=(6, 4))
sns.heatmap(
    confusion_matrix(y_test, y_pred),
    annot=True, fmt='d', cmap="Blues",
    xticklabels=["Not Expired", "Will Expire"],
    yticklabels=["Not Expired", "Will Expire"]
)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Spoilage Prediction Confusion Matrix")
plt.show()

# --- Step 10: Save model ---
joblib.dump(model, "spoilage_model.pkl")
print("Model saved as spoilage_model.pkl")

# --- Step 11: Verify saved model ---
loaded_model = joblib.load("spoilage_model.pkl")
print("Model reloaded successfully.")

# --- Step 12: Show 10 sample predictions ---
sample_results = X_test.copy()
sample_results["Actual_WillExpire"] = y_test.values
sample_results["Predicted_WillExpire"] = y_pred

# Reset index for clarity
sample_results = sample_results.reset_index(drop=True)

print("\nSample Predictions (10 rows):\n")
print(sample_results.head(10))

