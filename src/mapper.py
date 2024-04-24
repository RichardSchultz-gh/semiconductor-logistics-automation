from sqlalchemy import create_engine, Column, Integer, String, Date, TIMESTAMP, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Entities(Base):
    __tablename__ = 'entities'

    entity = Column(String(50), primary_key=True)
    class_ = Column('CLASS', String(50))
    enabled = Column(Integer)
    note = Column(String(50))
    state = Column('STATE',String(10))

class Lot(Base):
    __tablename__ = 'lot'

    lotid = Column(String(15), primary_key=True)
    priority = Column(Integer)
    pieces = Column(Integer)
    state = Column('STATE',String(15))
    product = Column(String(15))
    route = Column(String(15))
    oper = Column(String(15))
    customer = Column(String(15))
    order = Column('ORDER',String(15))
    duedate = Column(Date)
    startdate = Column(Date)
    enteroper = Column(TIMESTAMP)
    procstart = Column(TIMESTAMP)
    disptool = Column(String(10))

class ProdFlow(Base):
    __tablename__ = 'prodflow'

    product = Column(String(15), primary_key=True)
    route = Column(String(15), primary_key=True)
    seq = Column(Integer, primary_key=True)

class PTime(Base):
    __tablename__ = 'ptime'

    tool = Column(String(15), primary_key=True)
    product = Column(String(15), primary_key=True)
    route = Column(String(15), primary_key=True)
    oper = Column(String(15), primary_key=True)
    ptime = Column(Integer)
    int_ = Column('INT',Integer)

class Tool(Base):
    __tablename__ = 'tool'

    tool = Column(String(15), primary_key=True)
    toolfam = Column(String(15))
    owner = Column('OWNER',String(25))
    tooltype = Column(String(25))
    mttr = Column(Integer)
    mttf = Column(Integer)
    state = Column('STATE',String(15))

class Workflow(Base):
    __tablename__ = 'workflow'

    route = Column(String(15), primary_key=True)
    oper = Column(String(10), primary_key=True)
    desc = Column('DESC',String(255))
    mandatory = Column(Integer)
    stepperc = Column(DECIMAL(10, 2))