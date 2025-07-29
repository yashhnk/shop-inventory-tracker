-- Create the database (optional)
CREATE DATABASE IF NOT EXISTS InventoryTrackerDB;
USE KiranaInventoryDB;

-- 1. Suppliers Table
CREATE TABLE Suppliers (
    SupplierID INT PRIMARY KEY AUTO_INCREMENT,
    SupplierName VARCHAR(100) NOT NULL,
    Contact VARCHAR(20),
    Email VARCHAR(100),
    Address TEXT
);

-- 2. Products Table
CREATE TABLE Products (
    ProductID INT PRIMARY KEY AUTO_INCREMENT,
    ProductName VARCHAR(100) NOT NULL,
    Category VARCHAR(50),
    UnitPrice DECIMAL(10, 2) NOT NULL,
    SupplierID INT,
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID)
);

-- 3. Inventory Table
CREATE TABLE Inventory (
    InventoryID INT PRIMARY KEY AUTO_INCREMENT,
    ProductID INT,
    QuantityInStock INT NOT NULL,
    ExpiryDate DATE,
    LastRestocked DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

-- 4. Expiry_Alerts Table
CREATE TABLE Expiry_Alerts (
    AlertID INT PRIMARY KEY AUTO_INCREMENT,
    InventoryID INT,
    AlertDate DATE DEFAULT CURRENT_DATE,
    DaysBeforeExpiry INT,
    FOREIGN KEY (InventoryID) REFERENCES Inventory(InventoryID)
);

-- 5. Sales Table
CREATE TABLE Sales (
    SaleID INT PRIMARY KEY AUTO_INCREMENT,
    ProductID INT,
    QuantitySold INT NOT NULL,
    SaleDate DATE DEFAULT CURRENT_DATE,
    TotalAmount DECIMAL(10, 2),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

-- 6. Auto Reorder Rules Table (optional advanced)
CREATE TABLE Reorder_Rules (
    RuleID INT PRIMARY KEY AUTO_INCREMENT,
    ProductID INT,
    ReorderThreshold INT NOT NULL,
    ReorderQuantity INT NOT NULL,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);
