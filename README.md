# Smart Inventory + Expiry Tracker

A smart, database-driven inventory management system tailored for FMCG businesses. Features real-time expiry alerts, automated reordering, and ML-powered demand & spoilage predictions.

---

## Key Features

### Core DBMS Functionality
- **Products Management:** Add/edit/delete product data.
- **Inventory Monitoring:** Track stock levels, expiry dates, and restocking history.
- **Supplier Records:** Maintain supplier details and performance ratings.
- **Sales Tracking:** Capture daily sales across various payment modes.
- **Auto-Reorder System:** Automatically generate purchase orders when stock falls below threshold.
- **Expiry Alerts:** Get alerts for products nearing expiry using SQL views.

### Smart Additions (ML-Driven)
- **Sales Forecasting:** Predict future demand using historical sales data.
- **Spoilage Prediction:** Identify items likely to expire before being sold.
- **Dynamic Discounting:** Recommend discounts based on expiry proximity and demand.

---

## Database Schema Overview

### Tables
| Table | Key Columns |
|-------|-------------|
| `Products` | ProductID, Name, Category, UnitPrice, SupplierID, ReorderLevel |
| `Inventory` | ProductID, QuantityInStock, ExpiryDate, LastRestocked |
| `Suppliers` | SupplierID, Name, Contact, Rating |
| `Sales` | SaleID, ProductID, QuantitySold, Date, Mode |
| `ExpiryAlerts` | AlertID, ProductID, ExpiryDate, AlertGeneratedDate |
| `PurchaseOrders` | OrderID, ProductID, QuantityOrdered, OrderDate, SupplierID, Status |

### Views / Triggers
- `SoonToExpire`: View of products expiring in next 7 days
- Trigger: Auto-inserts into `PurchaseOrders` if stock < reorder level

---

## ⚙️ Technologies Used

| Component | Tools |
|----------|--------|
| DBMS     | MySQL / PostgreSQL |
| ML       | Python (pandas, scikit-learn, XGBoost) |
| Frontend (optional) | Flask / PHP + Bootstrap |
| Visualization | Matplotlib / Power BI / Tableau |

---

## ML Models

### 1. Sales Forecasting
- **Model:** Linear Regression / XGBoost
- **Features:** ProductID, week/month, past sales
- **Goal:** Predict next week's/month's demand

### 2. Spoilage Prediction
- **Model:** Binary Classification
- **Features:** Daily avg sales, expiry date, current stock
- **Goal:** Classify if item will expire before being sold

### 3. Discount Recommendation
- **Logic-based / Regression model**
- **Inputs:** Expiry proximity, demand, stock level
- **Output:** Suggested discount %

---

## UI Demo Screens (optional)

- Stock Overview Table
- Expiry Alerts Table
- Sales Charts & Demand Forecast
- Auto-Reorder Suggestions
- Spoilage Risk Items + Suggested Discounts

---

## Sample Visualizations

-  Line chart for monthly sales trends
-  Bar chart for spoilage vs. category
-  Table view for reorder & discount recommendations

---

## Resume Description (Add to CV)

> **Smart Inventory + Expiry Tracker** – Built a robust DBMS for real-time inventory tracking with automated reordering and expiry alerts. Integrated ML models to forecast sales, predict spoilage, and suggest discounts, reducing stock wastage and improving operational efficiency for small-scale FMCG setups.

---

## Setup Instructions

### Requirements
- MySQL/PostgreSQL
- Python 3.x
- pandas, scikit-learn, matplotlib
- Flask (optional)

Contributors
Aasavari Khire
Yash Khose
Drashi Manoria
