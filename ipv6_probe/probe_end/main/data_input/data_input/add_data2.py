import pickle
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

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


if __name__ == '__main__':
    # result为字典
    # '202.197.224.87':
    # ((('N', 'Error: timeout'), ('N', 'Error: timeout'), ('N', 'Error: timeout'), ('N', ''), ('N', ''), ('N', '')),
    # ['202.197.224.87', '湘潭大学仪器设备维修管理系统', '湘潭大学', '4143010530'])'
    with open('result.pkl', 'rb') as f:
        old_result = pickle.load(f)
        # 将url改成小写字母
        result = {}
        for k, v in old_result.items():
            result[k.lower()] = v
        print(len(result))

    with open('all_sites.pkl', 'rb') as f:
        all_sites = pickle.load(f)

    with open('prov.pkl', 'rb') as f:
        prov = pickle.load(f)

    # 现有数据加入省份
    q1 = Info.query.all()
    for q in q1:
        q.province = '江苏省'

    curr_sites = []
    for q in q1:
        curr_sites.append(q.url)


    for site in all_sites:
        if site in curr_sites:
            continue
        else:
            if site[:7] == 'http://':
                u = site[7:]
            elif site[:8] == 'https://':
                u = site[8:]
            else:
                u = site
            try:
                st = result[u][0]
                info = result[u][1]
            except KeyError:
                print(u)
            status = ['', '', '', '', '', '']
            for i, s in enumerate(st):
                if s[1] != '':
                    status[i] = s[1]
                else:
                    status[i] = s[0]

            # 省份信息
            try:
                p = prov[info[3]]
            except KeyError:
                p = ''
            if p != '':
                new_info = Info(unit=info[2], url=site, description=info[1], province=p)
            else:
                new_info = Info(unit=info[2], url=site, description=info[1])
            new_status = Status(http_v4=status[0], https_v4=status[1], http2_v4=status[2],
                                http_v6=status[3], https_v6=status[4], http2_v6=status[5])
            new_info.url_info = new_status
            db.session.add(new_info)
            db.session.add(new_status)

    db.session.commit()

    app.run()
