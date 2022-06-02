from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:159357@localhost/ipv6probe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


class Status(db.Model):

    __tablename__ = 'status'

    id = db.Column(db.Integer, primary_key=True)
    url_status = db.relationship('Info', back_populates='url_info')
    url_id = db.Column(db.Integer, db.ForeignKey('info.id'))

    http_v4 = db.Column(db.String(100))
    https_v4 = db.Column(db.String(100))
    http2_v4 = db.Column(db.String(100))
    http_v6 = db.Column(db.String(100))
    https_v6 = db.Column(db.String(100))
    http2_v6 = db.Column(db.String(100))

    # 以下均为预留
    bandwith = db.Column(db.Integer)  # 带宽
    flow = db.Column(db.Integer)  # 流量
    active = db.Column(db.Boolean)  # 是否活跃
    firewall = db.Column(db.Boolean)  # web防火墙
    has_cdn = db.Column(db.Boolean)  # 使用cdn
    server = db.Column(db.String(100))  # 服务器
    server_ver = db.Column(db.Float)  # 服务器版本


class Info(db.Model):

    __tablename__ = 'info'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200))
    unit = db.Column(db.String(100))  # 单位名称
    unit_type = db.Column(db.Integer)  # 预留，区分高校，中小学等
    belonging = db.Column(db.String(20))  # 预留，区分省属、部属等，暂时为空
    level = db.Column(db.String(20))  # 预留，区分985、211等，暂时为空
    province = db.Column(db.String(20))  # 省
    city = db.Column(db.String(20))  # 预留，市
    description = db.Column(db.String(300))
    open_status = db.Column(db.String(100))
    remark = db.Column(db.String(300))

    url_info = db.relationship('Status', uselist=False, back_populates='url_status')

'''
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
'''

if __name__ == '__main__':
    manager.run()
