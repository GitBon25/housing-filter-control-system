from sqlalchemy import Column, Integer, String, Numeric, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Apart(Base):
    __tablename__ = "apartments"
    

    id = Column(Integer, primary_key=True)
    description = Column(String)
    url = Column(String)
    price = Column(Integer)
    rooms = Column(Integer)
    area = Column(Numeric)
    floor = Column(Integer)
    location = Column(String)
    pics = ARRAY(String)