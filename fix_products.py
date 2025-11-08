import sqlite3

def fix_product_prices():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # First, show the current data
        print("\nCurrent products:")
        print("-" * 80)
        cursor.execute("SELECT id, name, price, is_available FROM api_product")
        for row in cursor.fetchall():
            print(f"ID: {row[0]}, Name: {row[1]}, Price: {row[2]}, Available: {bool(row[3])}")
        
        # Update the water bottle price
        cursor.execute("""
            UPDATE api_product 
            SET price = 1.50 
            WHERE name LIKE '%water bottle%' AND price = '1.5 liters water bottle'
        """)
        
        # Commit the changes
        conn.commit()
        print("\nUpdated water bottle price to 1.50")
        
        # Show the updated data
        print("\nUpdated products:")
        print("-" * 80)
        cursor.execute("SELECT id, name, price, is_available FROM api_product")
        for row in cursor.fetchall():
            print(f"ID: {row[0]}, Name: {row[1]}, Price: {row[2]}, Available: {bool(row[3])}")
        
        conn.close()
        print("\nPrice update complete. Please restart your Django server.")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fix_product_prices()
