from .database import Base, engine

def init_db():
    print("🔧 Creating tables if missing...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables ready!")
