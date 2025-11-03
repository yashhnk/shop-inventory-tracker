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
        database="SmartInventory",
        auth_plugin="mysql_native_password"
    )

# ---------------------------
# Load ML Models
# ---------------------------
demand_model = joblib.load("demandforecastingmodel.pkl")
spoilage_model = joblib.load("spoilage_model.pkl")

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
            p.Category AS category,       -- fixed the spelling
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
    sample_forecasts = [
        {"product": "Sushi Rice", "predictedDemand": 72.4},
        {"product": "Arabica Coffee", "predictedDemand": 85.6},
        {"product": "Greek Yogurt", "predictedDemand": 57.1},
        {"product": "Corn Oil", "predictedDemand": 63.9},
        {"product": "Plum", "predictedDemand": 60.4},
    ]
    return jsonify(sample_forecasts)





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
            p.UnitPrice,
            s.SupplierName,
            i.StockQuantity,
            i.ReorderLevel,
            i.ReorderQuantity
        FROM Products p
        JOIN Inventory i ON p.ProductID = i.ProductID
        LEFT JOIN Suppliers s ON p.SupplierID = s.SupplierID
        WHERE i.StockQuantity < i.ReorderLevel;
    """
    cursor.execute(query)
    items = cursor.fetchall()

    if not items:
        cursor.close()
        conn.close()
        return jsonify([])

    result = []
    for item in items:
        stock = item["StockQuantity"]
        reorder = item["ReorderLevel"]
        shortage_ratio = (reorder - stock) / reorder if reorder else 0

        # urgency level
        if shortage_ratio > 0.75:
            urgency = "critical"
        elif shortage_ratio > 0.5:
            urgency = "high"
        elif shortage_ratio > 0.25:
            urgency = "medium"
        else:
            urgency = "low"

        suggested_qty = item["ReorderQuantity"] or max(10, reorder - stock)
        total_amount = round(suggested_qty * float(item["UnitPrice"] or 0), 2)

        result.append({
            "ProductID": item["ProductID"],
            "ProductName": item["ProductName"],
            "SupplierName": item["SupplierName"],
            "StockQuantity": stock,
            "ReorderLevel": reorder,
            "suggestedQuantity": suggested_qty,
            "UnitPrice": float(item["UnitPrice"] or 0),
            "totalAmount": total_amount,
            "urgency": urgency,
            "EstimatedDelivery": "3-5 days"
        })

    cursor.close()
    conn.close()
    return jsonify(result)

@app.route('/api/pending_orders')
def pending_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            po.OrderID,
            p.ProductName,
            s.SupplierName,
            p.UnitPrice,
            po.QuantityOrdered,
            po.Status
        FROM PurchaseOrders po
        JOIN Products p ON po.ProductID = p.ProductID
        LEFT JOIN Suppliers s ON po.SupplierID = s.SupplierID
        WHERE po.Status = 'Pending'
        ORDER BY po.OrderDate DESC;
    """)
    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(orders)

@app.route('/api/recent_orders')
def recent_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            po.OrderID AS orderId,
            p.ProductName AS productName,
            s.SupplierName AS supplier,
            po.QuantityOrdered AS quantity,
            (po.QuantityOrdered * p.UnitPrice) AS amount,
            po.Status AS status
        FROM PurchaseOrders po
        JOIN Products p ON po.ProductID = p.ProductID
        LEFT JOIN Suppliers s ON po.SupplierID = s.SupplierID
        ORDER BY po.OrderDate DESC
        LIMIT 20;
    """)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(rows)


# ---------------------------
# Run Flask App
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
