from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:159357@localhost/ipv6probe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
    
if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    us1 = Hist_ele(id='1',province='江苏省')
    us2 = Hist_ele(id='2',province='陕西省')
    us3 = Hist_ele(id='3',province='上海市')
    us4 = Hist_ele(id='4',province='黑龙江省')
    us5 = Hist_ele(id='5', province='北京市')
    us6 = Hist_ele(id='6', province='天津市')
    us7 = Hist_ele(id='7', province='重庆市')
    us8 = Hist_ele(id='8', province='河北省')
    us9 = Hist_ele(id='9', province='山西省')
    us10 = Hist_ele(id='10', province='辽宁省')
    us11 = Hist_ele(id='11', province='吉林省')
    us12 = Hist_ele(id='12', province='浙江省')
    us13 = Hist_ele(id='13', province='安徽省')
    us14 = Hist_ele(id='14', province='福建省')
    us15 = Hist_ele(id='15', province='江西省')
    us16 = Hist_ele(id='16', province='山东省')
    us17 = Hist_ele(id='17', province='河南省')
    us18 = Hist_ele(id='18', province='湖北省')
    us19 = Hist_ele(id='19', province='广东省')
    us20 = Hist_ele(id='20', province='海南省')
    us21 = Hist_ele(id='21', province='四川省')
    us22 = Hist_ele(id='22', province='贵州省')
    us23 = Hist_ele(id='23', province='云南省')
    us24 = Hist_ele(id='24', province='青海省')
    us25 = Hist_ele(id='25', province='甘肃省')
    us26 = Hist_ele(id='26', province='湖南省')
    us27 = Hist_ele(id='27', province='台湾省')
    us28 = Hist_ele(id='28', province='内蒙古自治区')
    us29 = Hist_ele(id='29', province='广西壮族自治区')
    us30 = Hist_ele(id='30', province='西藏自治区')
    us31 = Hist_ele(id='31', province='宁夏回族自治区')
    us32 = Hist_ele(id='32', province='新疆维吾尔自治区')
    us33 = Hist_ele(id='33', province='香港特别行政区')
    us34 = Hist_ele(id='34', province='澳门特别行政区')

    db.session.add_all([us1,us2,us3,us4,us5,us6,us7,us8,us9,us10,us11,us12,us13,us14,us15,us16,us17,us18,us19,us20,us21,us22,us23,us24,us25,us26,us27,us28,us29,us30,us31,us32,us33,us34])
    db.session.commit()
    app.run(debug=True)