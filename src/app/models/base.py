from sqlalchemy import Column, BigInteger
from sqlalchemy_mixins import AllFeaturesMixin

from app.db.session import Base


class BaseDbModel(Base, AllFeaturesMixin):
    __abstract__ = True
    id = Column(BigInteger, primary_key=True)
