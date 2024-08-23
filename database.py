from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


from config import *

engine = create_engine(DB_URL, echo=DB_DEBUG)

Base = declarative_base()

Session = sessionmaker(bind=engine)
