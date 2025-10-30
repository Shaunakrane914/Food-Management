from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'sqlite:///./canteen_settings.db'

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BatchSetting(Base):
    __tablename__ = 'batch_settings'
    id = Column(Integer, primary_key=True, index=True)
    batch_name = Column(String, unique=True, index=True)
    total_count = Column(Integer)
    weekend_stay_percent = Column(Float)  # e.g., 0.95 for 95%

class ExamRule(Base):
    __tablename__ = 'exam_rules'
    id = Column(Integer, primary_key=True, index=True)
    exam_time = Column(String)  # e.g., '10:00'
    meal = Column(String)       # e.g., 'Breakfast', 'Dinner'
    reduction_percent = Column(Float)  # e.g., 0.5 for 50% reduction

class ExamDate(Base):
    __tablename__ = 'exam_dates'
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, unique=True, index=True)  # YYYY-MM-DD
    exam_time = Column(String)  # e.g., '10:00'

# Create tables
Base.metadata.create_all(bind=engine)

def initialize_default_batches():
    session = SessionLocal()
    if session.query(BatchSetting).count() == 0:
        defaults = [
            BatchSetting(batch_name="BBA", total_count=150, weekend_stay_percent=0.97),
            BatchSetting(batch_name="BTech", total_count=100, weekend_stay_percent=0.95),
            BatchSetting(batch_name="MBA", total_count=600, weekend_stay_percent=1.0),
        ]
        session.add_all(defaults)
        session.commit()
    session.close() 