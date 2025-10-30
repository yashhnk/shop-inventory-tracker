from flask_cors import CORS
from flask import Flask, jsonify
import mysql.connector
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---------------------------
# Database Connection
# ---------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="aneesh",
        database="SmartInventory"
    )

# ---------------------------
# Load ML Models
# ---------------------------
demand_model = joblib.load("demandforecastingmodel.pkl")
spoilage_model = joblib.load("spoilage_model (1).pkl")

# ---------------------------
# API 1: Get Products
# ---------------------------
@app.route('/api/products')
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            p.ProductID AS id,
            p.ProductName AS name,
            p.Catagory AS category,
            p.UnitPrice AS unitPrice,
            'Unknown' AS supplier,
            i.ReorderLevel AS reorderLevel,
            i.StockQuantity AS currentStock
        FROM Products p
        JOIN Inventory i ON p.ProductID = i.ProductID
        LIMIT 100;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    df = pd.DataFrame(rows).drop_duplicates(subset=["id"])

    for _, r in df.iterrows():
        if r['currentStock'] == 0:
            status = 'out-of-stock'
        elif r['currentStock'] < r['reorderLevel']:
            status = 'low-stock'
        else:
            status = 'active'
        df.loc[df['id'] == r['id'], 'status'] = status

    cursor.close()
    conn.close()
    return jsonify(df.to_dict(orient="records"))

# ---------------------------
# ✅ NEW API: Dashboard Metrics
# ---------------------------
@app.route('/api/dashboard_metrics')
def dashboard_metrics():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total Products
    cursor.execute("SELECT COUNT(*) AS totalProducts FROM Products;")
    total_products = cursor.fetchone()["totalProducts"]

    # Low Stock Items
    cursor.execute("""
        SELECT COUNT(*) AS lowStock
        FROM Inventory
        WHERE StockQuantity < ReorderLevel;
    """)
    low_stock = cursor.fetchone()["lowStock"]

    # Expiring Soon (within 7 days)
    cursor.execute("""
        SELECT COUNT(*) AS expiringSoon
        FROM Inventory
        WHERE ExpirationDate IS NOT NULL
          AND ExpirationDate BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY);
    """)
    expiring_soon = cursor.fetchone()["expiringSoon"]

    # Monthly Sales
    cursor.execute("""
        SELECT COALESCE(SUM(SalesVolume), 0) AS monthlySales
        FROM Sales
        WHERE MONTH(CURDATE()) = MONTH(NOW())
          AND YEAR(CURDATE()) = YEAR(NOW());
    """)
    monthly_sales = cursor.fetchone()["monthlySales"]

    cursor.close()
    conn.close()

    return jsonify({
        "totalProducts": total_products,
        "lowStock": low_stock,
        "expiringSoon": expiring_soon,
        "monthlySales": monthly_sales
    })

# ---------------------------
# API 2: Demand Forecast
# ---------------------------
@app.route('/api/demand_forecast')
def demand_forecast():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            p.ProductID,
            p.ProductName,
            i.StockQuantity,
            i.ReorderLevel,
            i.ReorderQuantity,
            p.UnitPrice,
            COALESCE(s.SalesVolume, 0) AS SalesVolume
        FROM Products p
        LEFT JOIN Inventory i ON p.ProductID = i.ProductID
        LEFT JOIN Sales s ON p.ProductID = s.ProductID
        LIMIT 100;
    """)

    products = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert to DataFrame and remove duplicates
    df = pd.DataFrame(products).drop_duplicates(subset=["ProductID"])
    df = df.fillna(0)  # handle any missing values

    # Ensure correct column order for prediction
    feature_cols = ["StockQuantity", "ReorderLevel", "ReorderQuantity", "UnitPrice", "SalesVolume"]

    forecasts = []
    for _, p in df.iterrows():
        try:
            features = np.array([[p[c] for c in feature_cols]], dtype=float)
            predicted_demand = float(demand_model.predict(features)[0])
        except Exception as e:
            print(f"Prediction error for {p['ProductName']}: {e}")
            predicted_demand = 0.0

        forecasts.append({
            "product": p["ProductName"] if p["ProductName"] else "Unknown",
            "predictedDemand": round(predicted_demand, 2)
        })

    return jsonify(forecasts)


# ---------------------------
# API 3: Spoilage Prediction
# ---------------------------
@app.route('/api/spoilage_prediction')
def spoilage_prediction():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.ProductID,
            p.ProductName,
            i.StockQuantity,
            i.ReorderLevel,
            i.ReorderQuantity,
            p.UnitPrice,
            s.SalesVolume,
            i.ExpirationDate,
            CASE 
                WHEN DATEDIFF(i.ExpirationDate, CURDATE()) > 0 
                THEN DATEDIFF(i.ExpirationDate, CURDATE()) 
                ELSE 0 
            END AS DaysRemaining,
            CASE 
                WHEN DATEDIFF(i.ExpirationDate, CURDATE()) > 0 AND s.SalesVolume IS NOT NULL
                THEN s.SalesVolume / DATEDIFF(i.ExpirationDate, CURDATE())
                ELSE 0
            END AS AvgDailySales
        FROM Products p
        LEFT JOIN Inventory i ON p.ProductID = i.ProductID
        LEFT JOIN Sales s ON p.ProductID = s.ProductID
        LIMIT 100;
    """)
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(products).drop_duplicates(subset=["ProductID"])
    df = df[df["StockQuantity"].notnull()]

    spoilage_data = []
    for _, p in df.iterrows():
        try:
            features = [[
                p["StockQuantity"] or 0,
                p["ReorderLevel"] or 0,
                p["ReorderQuantity"] or 0,
                float(p["UnitPrice"]) if p["UnitPrice"] else 0.0,
                p["SalesVolume"] or 0,
                p["DaysRemaining"] or 0,
                p["AvgDailySales"] or 0
            ]]
            predicted_spoilage = spoilage_model.predict(features)[0]
        except Exception:
            predicted_spoilage = 0

        spoilage_data.append({
            "product": p["ProductName"],
            "stock": int(p["StockQuantity"]),
            "daysLeft": int(p["DaysRemaining"]),
            "spoilageRisk": round(float(predicted_spoilage), 2)
        })

    return jsonify(spoilage_data)

# ---------------------------
# API 4: Auto Reorder
# ---------------------------
@app.route('/api/auto_reorder')
def auto_reorder():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT 
            p.ProductID,
            p.ProductName,
            p.SupplierID,
            i.StockQuantity,
            i.ReorderLevel,
            i.ReorderQuantity
        FROM Products p
        JOIN Inventory i ON p.ProductID = i.ProductID
        WHERE i.StockQuantity < i.ReorderLevel;
    """
    cursor.execute(query)
    low_stock_items = cursor.fetchall()

    if not low_stock_items:
        cursor.close()
        conn.close()
        return jsonify({"message": "All items are sufficiently stocked."})

    for item in low_stock_items:
        reorder_query = """
            INSERT INTO PurchaseOrders (ProductID, QuantityOrdered, OrderDate, SupplierID, Status)
            VALUES (%s, %s, CURDATE(), %s, 'Pending');
        """
        cursor.execute(reorder_query, (
            item['ProductID'],
            item['ReorderQuantity'],
            item['SupplierID']
        ))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "message": "Auto reorder triggered successfully.",
        "items": low_stock_items
    })

# ---------------------------
# Run Flask App
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
