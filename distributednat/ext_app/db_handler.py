"""
This is a handler of DB operations
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column
from sqlalchemy.types import CHAR
from sqlalchemy.ext.declarative import declarative_base


__all__ = ["DBError", "DBHandler"]


TOP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ENGINE = None
BaseModel = declarative_base()


class DBError(Exception):
    """ Exception that Database returns error """
    pass


class NATRule(BaseModel):
    """ Table of NAT rules """
    __tablename__ = 'nat_rule'

    int_ip = Column(CHAR(16), primary_key=True)
    ext_ip = Column(CHAR(16))


class DBHandler(object):
    """ Handler to CRUD BCNAT node table in DB """

    def __init__(self):
        engine = get_engine()
        DB_Session = sessionmaker(bind=engine)
        self.session = DB_Session()
        BaseModel.metadata.bind = engine
        BaseModel.metadata.create_all()

    def add(self, int_ip, ext_ip):
        """
        Add a NAT rule to DB
        """
        nat = NATRule(int_ip=int_ip, ext_ip=ext_ip)
        self.session.merge(nat)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise DBError(e)

    def delete(self, int_ip):
        """
        Delete a NAT rule
        """
        query = self.session.query(NATRule).filter(NATRule.int_ip == int_ip)
        map(self.session.delete, query)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise DBError(e)

    def get(self, int_ip=None, ext_ip=None):
        """ Filter and return NAT rules """
        query = self.session.query(NATRule)
        if int_ip is not None:
            query = query.filter(NATRule.int_ip == int_ip)
        if ext_ip is not None:
            query = query.filter(NATRule.ext_ip == ext_ip)
        try:
            ret = [dict(ext_ip=node.ext_ip, int_ip=node.int_ip)
                     for node in query.all()]
            return ret
        except Exception as e:
            raise DBError(e)


def get_engine():
    """ Singleton DB engine object """
    global ENGINE
    if ENGINE is None:
        DB_CONNECT_STRING = 'sqlite+pysqlite:///rules.db'
        ENGINE = create_engine(DB_CONNECT_STRING)
    return ENGINE
