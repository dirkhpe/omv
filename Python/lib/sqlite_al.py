# Consolidation for sqlite sqlalchemy related functions

from sqlalchemy import Column, Integer, ForeignKey, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()


class Component(Base):
    __tablename__ = "components"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    naam = Column(Text())
    category = Column(Text(), nullable=False)
    protege_id = Column(Text(), unique=True, nullable=False)
    label = Column(Text())
    commentaar = Column(Text())
    afdeling = Column(Text())
    artikel = Column(Text())
    bladzijde = Column(Text())
    hoofdstuk = Column(Text())
    onderafdeling = Column(Text())
    titel = Column(Text())
    titel_item = Column(Text())
    url = Column(Text())
    in_bereik = Column(Text())

    def __repr__(self):
        return "Component(ID: {prot_id} - Category: {cat} - naam: {naam})" .format(
            prot_id=self.protege_id,
            cat=self.category,
            naam=self.naam
        )


class Relation(Base):
    __tablename__ = "relations"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    rel_type = Column(Text())
    source = Column(Text(), ForeignKey('components.protege_id'))
    target = Column(Text(), ForeignKey('components.protege_id'))
    source_comp = relationship("Component", foreign_keys=[source])
    target_comp = relationship("Component", foreign_keys=[target])

    def __repr__(self):
        return "Relation({type}, From: {source} To: {target})".format(
            type=self.rel_type,
            source=self.source,
            target=self.target
        )


def set_engine(conn_string, echo=False):
    engine = create_engine(conn_string, echo=echo)
    return engine


def set_session4engine(engine):
    session_class = sessionmaker(bind=engine)
    session = session_class()
    return session


def init_session(db_loc="c:\\temp\\sql_al.sqlite3", echo=False):
    """
    This function configures the connection to the database and returns the session object.
    @param db_loc: Full path to the sqlite database.
    @param echo: True / False, depending if echo is required. Default: False
    @return: session object.
    """
    conn_string = "sqlite:///" + db_loc
    engine = set_engine(conn_string, echo)
    session = set_session4engine(engine)
    return session


if __name__ == "__main__":
    connstring = "sqlite:///c:\\temp\\sql_al.sqlite3"
    my_engine = set_engine(connstring, echo=False)
    Base.metadata.create_all(my_engine)
    my_session = set_session4engine(my_engine)

    for comp in my_session.query(Component):
        print(comp)

    for rel in my_session.query(Relation):
        print("{source} -[:{type}]-> {target}".format(source=rel.source_comp.naam,
                                                      type=rel.rel_type,
                                                      target=rel.target_comp.naam))
