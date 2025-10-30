-- Create Database
CREATE DATABASE SmartInventory;
USE SmartInventory;

-- 1. Suppliers Table
CREATE TABLE Suppliers (
    SupplierID VARCHAR(20) PRIMARY KEY,
    SupplierName VARCHAR(100) NOT NULL
);

-- 2. Products Table
CREATE TABLE Products (
    ProductID VARCHAR(20) PRIMARY KEY,
    ProductName VARCHAR(100) NOT NULL,
    Category VARCHAR(50),
    UnitPrice DECIMAL(10,2),
    SupplierID VARCHAR(20),
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID)
);

-- 3. Inventory Table
CREATE TABLE Inventory (
    InventoryID INT AUTO_INCREMENT PRIMARY KEY,
    ProductID VARCHAR(20),
    StockQuantity INT,
    ReorderLevel INT,
    ReorderQuantity INT,
    DateReceived DATE,
    LastOrderDate DATE,
    ExpirationDate DATE,
    WarehouseLocation VARCHAR(150),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

-- 4. Sales Table
CREATE TABLE Sales (
    SaleID INT AUTO_INCREMENT PRIMARY KEY,
    ProductID VARCHAR(20),
    SalesVolume INT,
    InventoryTurnoverRate INT,
    Status ENUM('Active','Discontinued','Backordered'),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

CREATE TABLE PurchaseOrders (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    ProductID VARCHAR(20),
    QuantityOrdered INT,
    OrderDate DATE,
    SupplierID VARCHAR(20),
    Status ENUM('Pending', 'Ordered', 'Received') DEFAULT 'Pending',
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID)
);


-- Expiry Alerts View
DROP VIEW IF EXISTS ExpiryAlerts;
CREATE VIEW ExpiryAlerts AS
SELECT i.InventoryID,
       i.ProductID,
       p.ProductName,
       i.StockQuantity,
       i.WarehouseLocation,
       i.ExpirationDate,
       DATEDIFF(i.ExpirationDate, CURDATE()) AS DaysLeft
FROM Inventory i
JOIN Products p ON i.ProductID = p.ProductID
WHERE i.ExpirationDate IS NOT NULL
  AND i.ExpirationDate BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)


DELIMITER $$

CREATE TRIGGER AutoReorder
AFTER UPDATE ON Inventory
FOR EACH ROW
BEGIN
    -- Check if stock fell below reorder level
    IF NEW.StockQuantity < NEW.ReorderLevel THEN
        INSERT INTO PurchaseOrders (
            ProductID,
            QuantityOrdered,
            OrderDate,
            SupplierID
        )
        VALUES (
            NEW.ProductID,
            NEW.ReorderQuantity,
            CURDATE(),
            (SELECT SupplierID FROM Products WHERE ProductID = NEW.ProductID)
        );
    END IF;
END $$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER ReduceInventoryOnSale
AFTER INSERT ON Sales
FOR EACH ROW
BEGIN
    UPDATE Inventory
    SET StockQuantity = GREATEST(StockQuantity - NEW.SalesVolume, 0),
        LastOrderDate = CURDATE()
    WHERE ProductID = NEW.ProductID;
END $$

DELIMITER ;
