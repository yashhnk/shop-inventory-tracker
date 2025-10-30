#!/usr/bin/env python
# coding: utf-8

import pymysql
import pandas as pd
import json

def get_expiry_alerts():
    """
    Fetch products expiring in the next 7 days from the ExpiryAlerts view.
    Returns a list of dictionaries (JSON-ready).
    """
    try:
        # --- Connect to MySQL ---
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="Yyaasshhnk#@2511",  # Replace with actual MySQL password
            database="SmartInventory",
            port=3306
        )

        # --- Read data using pandas ---
        df = pd.read_sql("SELECT * FROM ExpiryAlerts", conn)
        conn.close()

        # Convert date columns to string for JSON compatibility
        if 'ExpirationDate' in df.columns:
            df['ExpirationDate'] = df['ExpirationDate'].astype(str)

        # Convert dataframe to list of dictionaries
        alerts = df.to_dict(orient='records')
        return alerts

    except Exception as e:
        print("Error fetching expiry alerts:", e)
        return []

# --- Example usage ---
if __name__ == "__main__":
    alerts = get_expiry_alerts()
    if not alerts:
        print("No alerts found or error occurred.")
    else:
        # Print JSON-formatted output
        print(json.dumps(alerts, indent=4))
