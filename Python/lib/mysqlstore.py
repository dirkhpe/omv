# Consolidation for mysql related functions

import logging
import pymysql
from sqlalchemy import Column, Integer, String, Text, ForeignKey, create_engine, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()


class ArType(Base):
    __tablename__ = "artypes"
    id = Column(Integer, primary_key=True)
    protege_id = Column(String(256), unique=True, nullable=False)
    label = Column(String(256), nullable=False)
    naam = Column(String(256), nullable=False)
    commentaar = Column(Text())
    fases = relationship("ArFase",
                         secondary="arfase2type",
                         back_populates="types")
    artikels = relationship("WetArtikel",
                            secondary="type2artikel",
                            back_populates="types")
    upcomps = relationship("UpType",
                           secondary="artype2uptype",
                           back_populates="arcomps")

    def __repr__(self):
        return "Dossiertype(naam={t})".format(t=self.naam)


class ArFase(Base):
    __tablename__ = "arfases"
    id = Column(Integer, primary_key=True)
    protege_id = Column(String(256), unique=True, nullable=False)
    label = Column(String(256), nullable=False)
    naam = Column(String(256), nullable=False)
    commentaar = Column(Text())
    types = relationship("ArType",
                         secondary="arfase2type",
                         back_populates="fases")
    stappen = relationship("ArStap",
                           secondary="arstap2fase",
                           back_populates="fases")
    artikels = relationship("WetArtikel",
                            secondary="fase2artikel",
                            back_populates="fases")
    upcomps = relationship("UpFase",
                           secondary="arfase2upfase",
                           back_populates="arcomps")


class ArStap(Base):
    __tablename__ = "arstappen"
    id = Column(Integer, primary_key=True)
    protege_id = Column(String(256), unique=True, nullable=False)
    label = Column(String(256), nullable=False)
    naam = Column(String(256), nullable=False)
    commentaar = Column(Text())
    fases = relationship("ArFase",
                         secondary="arstap2fase",
                         back_populates="stappen")
    documenten = relationship("ArDocument",
                              secondary="ardocument2stap",
                              back_populates="stappen")
    artikels = relationship("WetArtikel",
                            secondary="stap2artikel",
                            back_populates="stappen")
    upcomps = relationship("UpStap",
                           secondary="arstap2upstap",
                           back_populates="arcomps")


class ArDocument(Base):
    __tablename__ = "ardocumenten"
    id = Column(Integer, primary_key=True)
    protege_id = Column(String(256), unique=True, nullable=False)
    label = Column(String(256), nullable=False)
    naam = Column(String(256), nullable=False)
    commentaar = Column(Text())
    stappen = relationship("ArStap",
                           secondary="ardocument2stap",
                           back_populates="documenten")
    artikels = relationship("WetArtikel",
                            secondary="document2artikel",
                            back_populates="documenten")
    upcomps = relationship("UpDocument",
                           secondary="ardocument2updocument",
                           back_populates="arcomps")


class ArFase2Type(Base):
    __tablename__ = "arfase2type"
    source_id = Column(Integer, ForeignKey('arfases.id'), primary_key=True)
    target_id = Column(Integer, ForeignKey('artypes.id'), primary_key=True)


class ArStap2Fase(Base):
    __tablename__ = "arstap2fase"
    source_id = Column(Integer, ForeignKey('arstappen.id'), primary_key=True)
    target_id = Column(Integer, ForeignKey('arfases.id'), primary_key=True)


class ArDocument2Stap(Base):
    __tablename__ = "ardocument2stap"
    source_id = Column(Integer, ForeignKey('ardocumenten.id'), primary_key=True)
    target_id = Column(Integer, ForeignKey('arstappen.id'), primary_key=True)


class WetBoek(Base):
    __tablename__ = "wetboeken"
    id = Column(Integer, primary_key=True)
    naam = Column(String(256), nullable=False)
    toc = relationship("WetToc", back_populates="boek")


class WetToc(Base):
    __tablename__ = "wettoc"
    id = Column(Integer, primary_key=True)
    boek_id = Column(Integer, ForeignKey('wetboeken.id'), nullable=False)
    titel = Column(Integer)
    hoofdstuk = Column(Integer)
    afdeling = Column(Integer)
    onderafdeling = Column(Integer)
    label = Column(String(256), nullable=False)
    item = Column(String(256), nullable=False)
    boek = relationship("WetBoek", back_populates="toc")
    artikels = relationship("WetArtikel", back_populates="toc")


class WetArtikel(Base):
    __tablename__ = "wetartikels"
    id = Column(Integer, primary_key=True)
    toc_id = Column(Integer, ForeignKey('wettoc.id'), nullable=False)
    artikel = Column(Integer, nullable=False)
    toc = relationship("WetToc", back_populates="artikels")
    types = relationship("ArType",
                         secondary="type2artikel",
                         back_populates="artikels")
    fases = relationship("ArFase",
                         secondary="fase2artikel",
                         back_populates="artikels")
    stappen = relationship("ArStap",
                           secondary="stap2artikel",
                           back_populates="artikels")
    documenten = relationship("ArDocument",
                              secondary="document2artikel",
                              back_populates="artikels")


class Type2Artikel(Base):
    __tablename__ = "type2artikel"
    protege_id = Column(String(256), ForeignKey('artypes.protege_id'), primary_key=True)
    artikel_id = Column(Integer, ForeignKey('wetartikels.id'), primary_key=True)


class Fase2Artikel(Base):
    __tablename__ = "fase2artikel"
    protege_id = Column(String(256), ForeignKey('arfases.protege_id'), primary_key=True)
    artikel_id = Column(Integer, ForeignKey('wetartikels.id'), primary_key=True)


class Stap2Artikel(Base):
    __tablename__ = "stap2artikel"
    protege_id = Column(String(256), ForeignKey('arstappen.protege_id'), primary_key=True)
    artikel_id = Column(Integer, ForeignKey('wetartikels.id'), primary_key=True)


class Document2Artikel(Base):
    __tablename__ = "document2artikel"
    protege_id = Column(String(256), ForeignKey('ardocumenten.protege_id'), primary_key=True)
    artikel_id = Column(Integer, ForeignKey('wetartikels.id'), primary_key=True)


class UpType(Base):
    __tablename__ = "uptypes"
    id = Column(Integer, primary_key=True)
    code = Column(String(256), nullable=False, unique=True)
    naam = Column(String(256), nullable=False)
    omercombi = relationship("OmerCombi", back_populates="uptype")
    arcomps = relationship("ArType",
                           secondary="artype2uptype",
                           back_populates="upcomps")


class UpFase(Base):
    __tablename__ = "upfases"
    id = Column(Integer, primary_key=True)
    code = Column(String(256), nullable=False, unique=True)
    naam = Column(String(256), nullable=False)
    weight = Column(Integer, nullable=False, default=25)
    omercombi = relationship("OmerCombi", back_populates="upfase")
    arcomps = relationship("ArFase",
                           secondary="arfase2upfase",
                           back_populates="upcomps")


class UpGebeurtenis(Base):
    __tablename__ = "upgebeurtenissen"
    id = Column(Integer, primary_key=True)
    code = Column(String(256), nullable=False, unique=True)
    naam = Column(String(256), nullable=False)
    upstap_id = Column(Integer, ForeignKey('upstappen.id'))
    upstap = relationship("UpStap", back_populates="upgebeurtenis")
    omercombi = relationship("OmerCombi", back_populates="upgebeurtenis")
    arcomps = relationship("UpDocument",
                           secondary="updocument2gebeurtenis",
                           back_populates="upcomps")


class UpStap(Base):
    __tablename__ = "upstappen"
    id = Column(Integer, primary_key=True)
    code = Column(String(256))
    naam = Column(String(256), nullable=False)
    upgebeurtenis = relationship("UpGebeurtenis", back_populates="upstap")
    arcomps = relationship("ArStap",
                           secondary="arstap2upstap",
                           back_populates="upcomps")


class UpDocument(Base):
    __tablename__ = "updocumenten"
    id = Column(Integer, primary_key=True)
    code = Column(String(256), nullable=False)
    naam = Column(String(256))
    source = Column(String(256))
    __table_args__ = (UniqueConstraint('code', 'source'),)
    omercombi = relationship("OmerCombi", back_populates="updocument")
    arcomps = relationship("ArDocument",
                           secondary="ardocument2updocument",
                           back_populates="upcomps")
    upcomps = relationship("UpGebeurtenis",
                           secondary="updocument2gebeurtenis",
                           back_populates="arcomps")


class UpDocument2Gebeurtenis(Base):
    __tablename__ = "updocument2gebeurtenis"
    updocument_id = Column(Integer, ForeignKey('updocumenten.id'), primary_key=True)
    upgebeurtenis_id = Column(Integer, ForeignKey('upgebeurtenissen.id'), primary_key=True)


class ArType2UpType(Base):
    __tablename__ = "artype2uptype"
    artype_id = Column(Integer, ForeignKey('artypes.id'), primary_key=True)
    uptype_id = Column(Integer, ForeignKey('uptypes.id'), primary_key=True)


class ArFase2UpFase(Base):
    __tablename__ = "arfase2upfase"
    arfase_id = Column(Integer, ForeignKey('arfases.id'), primary_key=True)
    upfase_id = Column(Integer, ForeignKey('upfases.id'), primary_key=True)


class ArStap2UpStap(Base):
    __tablename__ = "arstap2upstap"
    arstap_id = Column(Integer, ForeignKey('arstappen.id'), primary_key=True)
    upstap_id = Column(Integer, ForeignKey('upstappen.id'), primary_key=True)


class ArDocument2UpDocument(Base):
    __tablename__ = "ardocument2updocument"
    ardocument_id = Column(Integer, ForeignKey('ardocumenten.id'), primary_key=True)
    updocument_id = Column(Integer, ForeignKey('updocumenten.id'), primary_key=True)


class OmerCombi(Base):
    # Class to remember the valid combinations that are available in OMER.
    __tablename__ = "omercombi"
    id = Column(Integer, primary_key=True)
    uptype_id = Column(Integer, ForeignKey('uptypes.id'), nullable=False)
    upfase_id = Column(Integer, ForeignKey('upfases.id'), nullable=False)
    upgebeurtenis_id = Column(Integer, ForeignKey('upgebeurtenissen.id'), nullable=False)
    updocument_id = Column(Integer, ForeignKey('updocumenten.id'), nullable=False)
    bron = Column(String(256))
    __table_args__ = (UniqueConstraint('uptype_id', 'upfase_id', 'upgebeurtenis_id', 'updocument_id'),)
    uptype = relationship("UpType", back_populates="omercombi")
    upfase = relationship("UpFase", back_populates="omercombi")
    upgebeurtenis = relationship("UpGebeurtenis", back_populates="omercombi")
    updocument = relationship("UpDocument", back_populates="omercombi")


class DirectConn:
    """
    This class will set up a direct connection to MySQL. The purpose of the class is to reset the database vo_omv_ar.
    The current database will be dropped, then the new database will be created.
    Finally all tables will be created using SQLAlchemy library
    """

    def __init__(self, user, pwd):
        """
        The init procedure will set-up Connection to the Database Server, but not to a specific database.
        :param user:
        :param pwd:
        """
        mysql_conn = dict(
            host="localhost",
            port=3306,
            user=user,
            passwd=pwd
        )
        self.user = user
        self.pwd = pwd
        self.conn = pymysql.connect(**mysql_conn)
        self.cur = self.conn.cursor()

    def close(self):
        self.conn.close()

    def rebuild(self, db):
        """
        This function will drop and recreate the database. Then it will call SQLAlchemy to recreate the tables.
        :return:
        """
        query = "DROP DATABASE IF EXISTS {db}".format(db=db)
        logging.info(query)
        self.cur.execute(query)
        query = "CREATE DATABASE {db}".format(db=db)
        logging.info(query)
        self.cur.execute(query)
        # Now use sqlalchemy connection to build database
        conn_string = "mysql+pymysql://{u}:{p}@localhost/{db}".format(db=db, u=self.user, p=self.pwd)
        engine = set_engine(conn_string)
        Base.metadata.create_all(engine)

    def truncate_table(self, db, table):
        """
        This function will truncate a table.
        :param db:
        :param table:
        :return:
        """
        query = "USE {db}".format(db=db)
        self.cur.execute(query)
        query = "TRUNCATE TABLE {t}".format(t=table)
        self.cur.execute(query)
        return


def init_session(db, user, pwd, echo=False):
    """
    This function configures the connection to the database and returns the session object.

    :param db: Name of the MySQL database.

    :param user: User for the connection.

    :param pwd: Connection password associated with this user.

    :param echo: True / False, depending if echo is required. Default: False

    :return: session object.
    """
    # conn_string = "mysql+pymysql://{u}:{p}@localhost/{db}?charset=utf8&use_unicode=0".format(db=db, u=user, p=pwd)
    conn_string = "mysql+pymysql://{u}:{p}@localhost/{db}?charset=utf8".format(db=db, u=user, p=pwd)
    engine = set_engine(conn_string, echo)
    session = set_session4engine(engine)
    return session


def set_engine(conn_string, echo=False):
    engine = create_engine(conn_string, echo=echo)
    return engine


def set_session4engine(engine):
    session_class = sessionmaker(bind=engine)
    session = session_class()
    return session


if __name__ == "__main__":
    connstring = "mysql+pymysql://root:Monitor1@localhost/vo_omv_ar"
    my_engine = set_engine(connstring, echo=False)
    Base.metadata.create_all(my_engine)
    my_session = set_session4engine(my_engine)

    for ar_type in my_session.query(ArType):
        print(ar_type)
