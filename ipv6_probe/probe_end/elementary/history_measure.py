from flask import render_template, url_for, redirect, flash, current_app, request,session
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import time


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:159357@localhost/ipv6probe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Status_be(db.Model):

    __tablename__ = 'status'

    id = db.Column(db.Integer, primary_key=True)
    url_status = db.relationship('Info_be', back_populates='url_info_be')
    url_id = db.Column(db.Integer, db.ForeignKey('info_be.id'))

    http_v4 = db.Column(db.String(100))
    https_v4 = db.Column(db.String(100))
    http2_v4 = db.Column(db.String(100))
    http_v6 = db.Column(db.String(100))
    https_v6 = db.Column(db.String(100))
    http2_v6 = db.Column(db.String(100))





class Info_be(db.Model):

    __tablename__ = 'info_be'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500))
    description = db.Column(db.String(500))
    unit_name = db.Column(db.String(500))
    unit_code = db.Column(db.String(8000))
    title = db.Column(db.String(500))
    up_unit_code = db.Column(db.String(8000))
    up_unit_code1 = db.Column(db.String(8000))
    up_unit_code2 = db.Column(db.String(8000))
    up_unit_code3 = db.Column(db.String(500))

    url_info_be = db.relationship('Status_be', uselist=False, back_populates='url_status')

class Hist_ele(db.Model):
    __tablename__ = 'hist_ele'
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

class Pro(db.Model):
    __tablename__ = 'pro'
    id = db.Column(db.Integer, primary_key=True)
    unit_name = db.Column(db.String(500))
    alert = db.Column(db.String(500))


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
    result=Hist_ele.query.all()

    for r in result:     
        kw=r.province  
        p = Pro.query.filter(Pro.unit_name.like(kw)).first()
        kv = p.alert
        result1 = Info_be.query.filter(or_((Info_be.up_unit_code==kv),(Info_be.up_unit_code1==kv),
                                         (Info_be.up_unit_code2==kv),(Info_be.up_unit_code3==kv)))
        Count1 = 0
        for t in result1:
            if ((t.url_info_be.http_v6 == 'Y') | (t.url_info_be.https_v6 == 'Y') | (t.url_info_be.http2_v6 == 'Y')):
                Count1 = Count1 + 1

        sql='update hist_ele set '+ b +' ='+str(Count1)+' where id='+str(r.id)+''
        db.session.execute(sql)
        db.session.commit()


if __name__ == '__main__':
    measure()

