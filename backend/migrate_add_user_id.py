import sqlite3
from services.database import DATABASE_URL

def migrate():
    db_path = DATABASE_URL.replace("sqlite:///", "")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Adding user_id columns...")
    
    try:
        # Add user_id to customers
        try:
            cursor.execute("ALTER TABLE customers ADD COLUMN user_id INTEGER REFERENCES users(id)")
            print("Added user_id to customers")
        except sqlite3.OperationalError as e:
            print("customers.user_id already exists or error:", e)
        
        # Add user_id to products
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN user_id INTEGER REFERENCES users(id)")
            print("Added user_id to products")
        except sqlite3.OperationalError as e:
            print("products.user_id already exists or error:", e)
        
        # Add user_id to invoices
        try:
            cursor.execute("ALTER TABLE invoices ADD COLUMN user_id INTEGER REFERENCES users(id)")
            print("Added user_id to invoices")
        except sqlite3.OperationalError as e:
            print("invoices.user_id already exists or error:", e)
        
        # Add user_id to expenses
        try:
            cursor.execute("ALTER TABLE expenses ADD COLUMN user_id INTEGER REFERENCES users(id)")
            print("Added user_id to expenses")
        except sqlite3.OperationalError as e:
            print("expenses.user_id already exists or error:", e)
        
        conn.commit()
        print("Migration complete!")
        
    except Exception as e:
        conn.rollback()
        print("Migration failed:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
