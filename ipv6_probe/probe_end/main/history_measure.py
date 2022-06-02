from flask import render_template, url_for, redirect, flash, current_app, request,session
from flask import Flask
from sqlalchemy import or_
from flask_sqlalchemy import SQLAlchemy
import time


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:159357@localhost/ipv6probe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

class Hist(db.Model):
    __tablename__ = 'hist'
    id = db.Column(db.Integer, primary_key=True)
    province = db.Column(db.String(20))
    january = db.Column(db.Integer)
    february = db.Column(db.Integer)
    march = db.Column(db.Integer)
    april = db.Column(db.Integer)
    may = db.Column(db.Integer)
    june = db.Column(db.Integer)
    july = db.Column(db.Integer)
    august = db.Column(db.Integer)
    september = db.Column(db.Integer)
    october = db.Column(db.Integer)
    november = db.Column(db.Integer)
    december = db.Column(db.Integer)



def measure():               ##测量每个省份v6通的情况，并记入count1中
    localtime = time.localtime(time.time())
    if localtime.tm_mon == 1:
        b = 'january'
    if localtime.tm_mon == 2:
        b = 'february'
    if localtime.tm_mon == 3:
        b = 'march'
    if localtime.tm_mon == 4:
        b = 'april'
    if localtime.tm_mon == 5:
        b = 'may'
    if localtime.tm_mon == 6:
        b = 'june'
    if localtime.tm_mon == 7:
        b = 'july'
    if localtime.tm_mon == 8:
        b = 'august'
    if localtime.tm_mon == 9:
        b = 'september'
    if localtime.tm_mon == 10:
        b = 'october'
    if localtime.tm_mon == 11:
        b = 'november'
    if localtime.tm_mon == 12:
        b = 'december'
    result=Hist.query.all()
    for r in result:       
        result1 = Info.query.filter(Info.province.like(r.province))
        Count1 = 0
        for t in result1:
            if ((t.url_info.http_v6 == 'Y') | (t.url_info.https_v6 == 'Y') | (t.url_info.http2_v6 == 'Y')):
                Count1 = Count1 + 1
        sql='update hist set '+ b +' ='+str(Count1)+' where id='+str(r.id)+''
        db.session.execute(sql)
        db.session.commit()


if __name__ == '__main__':
    measure()

