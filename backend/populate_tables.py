#!/usr/bin/env python
# coding: utf-8

import pymysql
import pandas as pd
import datetime

# --- MySQL Connection ---
try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="aneesh",  # change if needed
        database="SmartInventory",
        port=3306,
        autocommit=False
    )
    cursor = conn.cursor()
    print("✅ Database connection successful!")
except Exception as e:
    print("❌ Connection error:", e)
    exit(1)

# --- Load Dataset ---
df = pd.read_csv("Grocery_Inventory_and_Sales_Dataset_Cleaned.csv")

# --- Convert date columns (DD/MM/YYYY → YYYY-MM-DD) ---
date_cols = ['Date_Received', 'Last_Order_Date', 'Expiration_Date']
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')

# Ensure dates are valid and in ISO format
for col in date_cols:
    if col in df.columns:
        df[col] = df[col].dt.strftime('%Y-%m-%d')

# --- Drop duplicate rows (avoid double insertion) ---
df = df.drop_duplicates(subset=['Product_ID', 'Expiration_Date'])

# --- Helper Functions ---
def noneify(lst):
    """Convert NaN to None for MySQL compatibility"""
    return [None if pd.isna(x) or x == '' else x for x in lst]

def insert_batches(cursor, query, data, batch_size=100):
    total = len(data)
    for start in range(0, total, batch_size):
        batch = data[start:start + batch_size]
        cursor.executemany(query, batch)
        print(f"Inserted rows {start + 1} to {start + len(batch)}")

# --- 1. Suppliers Table ---
suppliers = df[['Supplier_ID', 'Supplier_Name']].drop_duplicates()
suppliers_list = [noneify(row) for row in suppliers.values.tolist()]
insert_batches(cursor,
    "INSERT IGNORE INTO Suppliers (SupplierID, SupplierName) VALUES (%s, %s)",
    suppliers_list)

# --- 2. Products Table ---
products = df[['Product_ID', 'Product_Name', 'Catagory', 'Unit_Price', 'Supplier_ID']].drop_duplicates()
products.rename(columns={
    'Product_ID': 'ProductID',
    'Product_Name': 'ProductName',
    'Catagory': 'Catagory',  # keep your original column spelling
    'Unit_Price': 'UnitPrice',
    'Supplier_ID': 'SupplierID'
}, inplace=True)

products_list = [noneify(row) for row in products.values.tolist()]
insert_batches(cursor,
    "INSERT IGNORE INTO Products (ProductID, ProductName, Category, UnitPrice, SupplierID) VALUES (%s, %s, %s, %s, %s)",
    products_list)

# --- 3. Inventory Table ---
inventory_cols = [
    'Product_ID', 'Stock_Quantity', 'Reorder_Level', 'Reorder_Quantity',
    'Date_Received', 'Last_Order_Date', 'Expiration_Date', 'Warehouse_Location'
]
inventory = df[inventory_cols].drop_duplicates(subset=['Product_ID'])
inventory.rename(columns={
    'Product_ID': 'ProductID',
    'Stock_Quantity': 'StockQuantity',
    'Reorder_Level': 'ReorderLevel',
    'Reorder_Quantity': 'ReorderQuantity',
    'Date_Received': 'DateReceived',
    'Last_Order_Date': 'LastOrderDate',
    'Expiration_Date': 'ExpirationDate',
    'Warehouse_Location': 'WarehouseLocation'
}, inplace=True)

inventory_list = [noneify(row) for row in inventory.values.tolist()]
insert_batches(cursor,
    """INSERT INTO Inventory (ProductID, StockQuantity, ReorderLevel, ReorderQuantity,
                              DateReceived, LastOrderDate, ExpirationDate, WarehouseLocation)
       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
    inventory_list)

# --- 4. Sales Table ---
sales_cols = ['Product_ID', 'Sales_Volume', 'Inventory_Turnover_Rate', 'Status']
sales = df[sales_cols].drop_duplicates(subset=['Product_ID'])
sales.rename(columns={
    'Product_ID': 'ProductID',
    'Sales_Volume': 'SalesVolume',
    'Inventory_Turnover_Rate': 'InventoryTurnoverRate',
    'Status': 'Status'
}, inplace=True)

sales_list = [noneify(row) for row in sales.values.tolist()]
insert_batches(cursor,
    "INSERT INTO Sales (ProductID, SalesVolume, InventoryTurnoverRate, Status) VALUES (%s, %s, %s, %s)",
    sales_list)

# --- 5. Purchase Orders (Auto-generated for low stock) ---
po_df = df[['Product_ID', 'Supplier_ID', 'Stock_Quantity', 'Reorder_Level', 'Reorder_Quantity']].drop_duplicates()
purchase_orders = []
today = datetime.date.today()

for _, row in po_df.iterrows():
    if pd.notna(row['Reorder_Level']) and pd.notna(row['Stock_Quantity']):
        if row['Stock_Quantity'] <= row['Reorder_Level']:
            purchase_orders.append((
                row['Product_ID'],
                int(row['Reorder_Quantity']) if not pd.isna(row['Reorder_Quantity']) else 10,
                today,
                row['Supplier_ID'],
                'Pending'
            ))

if purchase_orders:
    cursor.executemany("""
        INSERT INTO PurchaseOrders (ProductID, QuantityOrdered, OrderDate, SupplierID, Status)
        VALUES (%s, %s, %s, %s, %s)
    """, purchase_orders)
    print(f"Inserted {len(purchase_orders)} purchase orders.")
else:
    print("No purchase orders triggered (stock levels sufficient).")

# --- Commit and Close ---
conn.commit()
cursor.close()
conn.close()
print("Batch insert completed successfully!")

# --- Verify inserted data ---
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="aneesh",
    database="SmartInventory",
    port=3306
)

tables = ['Suppliers', 'Products', 'Inventory', 'Sales', 'PurchaseOrders']
for table in tables:
    print(f"\n--- {table} ---")
    df_preview = pd.read_sql(f"SELECT * FROM {table} LIMIT 5", conn)
    print(df_preview)

conn.close()
