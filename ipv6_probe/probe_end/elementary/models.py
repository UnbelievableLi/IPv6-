from sqlalchemy import Column, String, Integer, create_engine, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql+psycopg2://postgres:159357@localhost/ipv6probe')
Session = sessionmaker(bind=engine)

Base = declarative_base()



class Status_be(Base):

    __tablename__ = 'status_be'

    id = Column(Integer, primary_key=True)
    url_status = relationship('Info_be', back_populates='url_info_be')
    url_id = Column(Integer, ForeignKey('info_be.id'))

    http_v4 = Column(String(100))
    https_v4 = Column(String(100))
    http2_v4 = Column(String(100))
    http_v6 = Column(String(100))
    https_v6 = Column(String(100))
    http2_v6 = Column(String(100))


class Hist_ele(Base):
    __tablename__ = 'hist_ele'
    id = Column(Integer, primary_key=True)
    province = Column(String(20))
    january = Column(Integer)
    february = Column(Integer)
    march = Column(Integer)
    april = Column(Integer)
    may = Column(Integer)
    june = Column(Integer)
    july = Column(Integer)
    august = Column(Integer)
    september = Column(Integer)
    october = Column(Integer)
    november = Column(Integer)
    december = Column(Integer)

class Info_be(Base):

    __tablename__ = 'info_be'

    id = Column(Integer, primary_key=True)
    url = Column(String(500))
    description = Column(String(500))
    unit_name = Column(String(500))
    unit_code = Column(String(8000))
    title = Column(String(500))
    up_unit_code = Column(String(8000))
    up_unit_code1 = Column(String(8000))
    up_unit_code2 = Column(String(8000))
    up_unit_code3 = Column(String(500))


    url_info_be = relationship('Status_be', uselist=False, back_populates='url_status')

class Pro(Base):

    __tablename__ = 'pro'

    id = Column(Integer, primary_key=True)
    unit_name = Column(String(500))
    alert = Column(String(500))







if __name__ == '__main__':
    Base.metadata.create_all(engine)
