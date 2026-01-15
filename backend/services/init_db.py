from services.database import engine, Base
from services import models  # IMPORTANT: registers all models

def init_db():
    Base.metadata.create_all(bind=engine)
