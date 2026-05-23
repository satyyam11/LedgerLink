import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def migrate():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print(f"Using database URL from DATABASE_URL")
    else:
        from services.database import DATABASE_URL as default_url
        database_url = default_url
    
    print(f"Connecting to database...")
    
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            print("Adding name column to users table...")
            
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR"))
                conn.commit()
                print("Successfully added name column!")
            except Exception as e:
                if "column \"name\" of relation \"users\" already exists" in str(e):
                    print("name column already exists, skipping.")
                else:
                    print(f"Error: {e}")
                    conn.rollback()
                    raise
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
