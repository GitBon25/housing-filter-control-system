from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ApartUrl(Base):
    __tablename__ = "apartmentsURL"
    id = Column(Integer, primary_key=True)
    url = Column(String)
    
class Apart(Base):
    tableName = "apartments"
    

    id = Column(Integer, primary_key=True)
    description = Column(String)
    url = Column(String)
    price = Column(Integer)
    rooms = Column(Integer)
    area = Column(Integer)
    floor = Column(Integer)
    location = Column(String)
    parsing_date = Column(Date)