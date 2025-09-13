#!/usr/bin/env python
# coding: utf-8

# In[14]:


import pymysql
import pandas as pd

# --- DB connection ---
try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD_HERE",
        database="SmartInventory",
        port=3306,
        autocommit=False  # Commit manually
    )
    cursor = conn.cursor()
    print("Connection successful!")
except Exception as e:
    print("Connection error:", e)
    exit(1)

# --- Load dataset ---
df = pd.read_csv("Grocery_Inventory_and_Sales_Dataset_Cleaned.csv")

# --- Convert date columns (DD/MM/YYYY → YYYY-MM-DD) ---
date_cols = ['Date_Received', 'Last_Order_Date', 'Expiration_Date']
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

# --- Helper functions ---
def noneify(lst):
    """Convert NaN to None for MySQL compatibility"""
    return [None if pd.isna(x) else x for x in lst]

def insert_batches(cursor, query, data, batch_size=100):
    total = len(data)
    for start in range(0, total, batch_size):
        batch = data[start:start+batch_size]
        cursor.executemany(query, batch)
        print(f"Inserted rows {start+1} to {start+len(batch)}")

# --- Suppliers ---
suppliers = df[['Supplier_ID', 'Supplier_Name']].drop_duplicates()
suppliers_list = [noneify(row) for row in suppliers.values.tolist()]
insert_batches(cursor, 
               "INSERT IGNORE INTO Suppliers (SupplierID, SupplierName) VALUES (%s, %s)", 
               suppliers_list)

# --- Products ---
products = df[['Product_ID', 'Product_Name', 'Catagory', 'Unit_Price', 'Supplier_ID']].drop_duplicates()
products_list = [noneify(row) for row in products.values.tolist()]
insert_batches(cursor, 
               "INSERT IGNORE INTO Products (ProductID, ProductName, Category, UnitPrice, SupplierID) VALUES (%s, %s, %s, %s, %s)", 
               products_list)

# --- Inventory ---
inventory_cols = ['Product_ID', 'Stock_Quantity', 'Reorder_Level', 'Reorder_Quantity',
                  'Date_Received', 'Last_Order_Date', 'Expiration_Date', 'Warehouse_Location']
inventory = df[inventory_cols]
inventory_list = [noneify(row) for row in inventory.values.tolist()]
insert_batches(cursor, 
               """INSERT INTO Inventory (ProductID, StockQuantity, ReorderLevel, ReorderQuantity,
                                        DateReceived, LastOrderDate, ExpirationDate, WarehouseLocation)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", 
               inventory_list)

# --- Sales ---
sales_cols = ['Product_ID', 'Sales_Volume', 'Inventory_Turnover_Rate', 'Status']
sales = df[sales_cols]
sales_list = [noneify(row) for row in sales.values.tolist()]
insert_batches(cursor, 
               "INSERT INTO Sales (ProductID, SalesVolume, InventoryTurnoverRate, Status) VALUES (%s, %s, %s, %s)", 
               sales_list)

# --- Commit and close ---
conn.commit()
cursor.close()
conn.close()

print("Batch insert completed successfully!")


# In[15]:


import pymysql
import pandas as pd

# --- Connect to MySQL ---
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="aneesh",
    database="SmartInventory",
    port=3306
)

tables = ['Suppliers', 'Products', 'Inventory', 'Sales']

for table in tables:
    print(f"\n--- {table} ---")
    df = pd.read_sql(f"SELECT * FROM {table} LIMIT 10", conn)  # shows first 10 rows
    print(df)

conn.close()


# In[ ]:




