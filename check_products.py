import sqlite3
import os

def check_products():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Get the list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print("\nTables in database:")
        print("-" * 50)
        for table in cursor.fetchall():
            print(table[0])
        
        # Check if api_product table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_product';")
        if not cursor.fetchone():
            print("\nError: 'api_product' table not found in the database!")
            return
        
        # Get column names for api_product
        cursor.execute("PRAGMA table_info(api_product)")
        columns = [column[1] for column in cursor.fetchall()]
        print("\nColumns in api_product table:")
        print("-" * 50)
        print("\n".join(columns))
        
        # Get all products
        cursor.execute("SELECT * FROM api_product")
        products = cursor.fetchall()
        
        print(f"\nFound {len(products)} products:")
        print("-" * 100)
        print("ID  | Name                              | Price    | Category    | Available | Stock | Created At")
        print("-" * 100)
        
        for product in products:
            # Format the output based on available columns
            product_id = product[0]
            name = str(product[1])[:30].ljust(30)  # Truncate and pad name
            price = f"{float(product[2]):.2f}".rjust(8) if product[2] is not None else "N/A"
            category = str(product[3])[:10].ljust(10) if len(product) > 3 else "N/A"
            is_available = str(bool(product[4])) if len(product) > 4 else "N/A"
            stock = str(product[5]) if len(product) > 5 else "N/A"
            created_at = str(product[6])[:16] if len(product) > 6 else "N/A"
            
            print(f"{str(product_id).ljust(3)} | {name} | {price} | {category} | {str(is_available).ljust(9)} | {str(stock).ljust(5)} | {created_at}")
        
        conn.close()
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_products()
