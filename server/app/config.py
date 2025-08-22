import os
from dotenv import load_dotenv


load_dotenv()

# Get DATABASE_URL directly from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback: Construct from individual parts if DATABASE_URL not set
if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    
    if all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        raise ValueError("Either DATABASE_URL or all individual DB_* variables must be set")
