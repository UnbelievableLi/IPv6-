from sqlalchemy import Column, String, Integer, create_engine, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql+psycopg2://postgres:159357@localhost/ipv6probe')
Session = sessionmaker(bind=engine)

Base = declarative_base()


class Status(Base):

    __tablename__ = 'status'

    id = Column(Integer, primary_key=True)
    url_status = relationship('Info', back_populates='url_info')
    url_id = Column(Integer, ForeignKey('info.id'))

    http_v4 = Column(String(100))
    https_v4 = Column(String(100))
    http2_v4 = Column(String(100))
    http_v6 = Column(String(100))
    https_v6 = Column(String(100))
    http2_v6 = Column(String(100))


class Info(Base):

    __tablename__ = 'info'

    id = Column(Integer, primary_key=True)
    url = Column(String(200))
    unit = Column(String(100))
    description = Column(String(300))
    open_status = Column(String(100))
    remark = Column(String(300))

    url_info = relationship('Status', uselist=False, back_populates='url_status')


class IP(Base):

    __tablename__ = 'ip'

    id = Column(Integer, primary_key=True)
    unit = Column(String(100))
    address_begin = Column(INET)
    address_end = Column(INET)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, index=True)
    password_hash = Column(String(128))
	
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


Base.metadata.create_all(engine)

