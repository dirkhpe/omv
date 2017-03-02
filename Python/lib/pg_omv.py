"""
This module consolidates the communication with Postgres database Omgevingsvergunning
"""
import sys
import logging
from sqlalchemy import Column, Integer, String, Text, ForeignKey, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import ArgumentError

if __name__ == "__main__":
    conn_string = "postgresql://postgres:R1NUY1k-oKGG@localhost:5432/omv2db"
    engine = create_engine(conn_string)
    meta = MetaData(schema='omv')
    Base = automap_base(bind=engine, metadata=meta)
    try:
        Base.prepare(engine, reflect=True)
    except ArgumentError:
        pass
    print("Tables: {t}".format(t=Base.classes.keys()))
    tp_dossierstuktype = Base.classes.tp_dossierstuktype
    print("Table: {t}".format(t=tp_dossierstuktype))
    session_class = sessionmaker(bind=engine)
    session = session_class()
    for rec in session.query(tp_dossierstuktype):
        print("{dt}".format(dt=rec.dossierstuktype))
