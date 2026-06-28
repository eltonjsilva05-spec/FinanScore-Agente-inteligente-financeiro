from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Date,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    tipo = Column(String)
    categoria = Column(String)
    descricao = Column(String)
    valor = Column(Float)
    data = Column(Date)