from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

engine = create_engine('sqlite:///events.db')
Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    title = Column(String)
    img = Column(String)
    date = Column(String)
    time = Column(String)
    place = Column(String)
    price = Column(String)
    attendees = Column(String)

Base.metadata.create_all(bind=engine)