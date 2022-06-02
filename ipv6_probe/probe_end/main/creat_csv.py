import numpy as np
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os, sys, stat

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


class Status_be(db.Model):

    __tablename__ = 'status_be'

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


## 导出高校信息的表
all_info = Info.query.all()                  
all_status = Status.query.all()
length=len(all_info)                        #表的行数，即url数


unit_url_one=[]
status_one=[]
result_csv = []

for i, s in enumerate(all_info):
    unit_url_one.append(s.unit)
    unit_url_one.append(s.url)



for i, s in enumerate(all_status):
    status_one.append(s.http_v4)
    status_one.append(s.https_v4)
    status_one.append(s.http2_v4)
    status_one.append(s.http_v6)
    status_one.append(s.https_v6)
    status_one.append(s.http2_v6)

for index in range(length):
    result_csv.append([unit_url_one[index*2], unit_url_one[index*2 + 1], status_one[index*6],status_one[index*6 + 1],
    status_one[index*6 + 2],status_one[index*6 + 3],status_one[index*6 + 4],status_one[index*6 + 5]])


name=['单位','URL','http/IPv4','https/IPv4','http2/IPv4','http/Ipv6','https/IPv6','http2/IPv6']
result=pd.DataFrame(columns=name,data=result_csv)
result.to_csv('result.csv',encoding='utf-8-sig')



## 导出基础教育信息的表
all_info_be = Info_be.query.all()                  
all_status_be = Status_be.query.all()
length_be=len(all_info_be)                        #表的行数，即url数


unit_url_one_be=[]
status_one_be=[]
result_csv_be = []

for i, s in enumerate(all_info_be):
    unit_url_one_be.append(s.unit_name)
    unit_url_one_be.append(s.url)



for i, s in enumerate(all_status_be):
    status_one_be.append(s.http_v4)
    status_one_be.append(s.https_v4)
    status_one_be.append(s.http2_v4)
    status_one_be.append(s.http_v6)
    status_one_be.append(s.https_v6)
    status_one_be.append(s.http2_v6)

for index in range(length_be):
    result_csv_be.append([unit_url_one_be[index*2], unit_url_one_be[index*2 + 1], status_one_be[index*6],status_one_be[index*6 + 1],
    status_one_be[index*6 + 2],status_one_be[index*6 + 3],status_one_be[index*6 + 4],status_one_be[index*6 + 5]])


name=['单位','URL','http/IPv4','https/IPv4','http2/IPv4','http/Ipv6','https/IPv6','http2/IPv6']
result_be=pd.DataFrame(columns=name,data=result_csv_be)
result_be.to_csv('result_be.csv',encoding='utf-8-sig')