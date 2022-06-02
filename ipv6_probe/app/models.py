from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager


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


class Ping(db.Model):
    __tablename__ = 'ping'
    id = db.Column(db.Integer, primary_key=True)
    province = db.Column(db.String(20))
    count = db.Column(db.Integer)

class School(db.Model):
    __tablename__ = 'school'
    id = db.Column(db.Integer, primary_key=True)
    school = db.Column(db.String(100))
    count = db.Column(db.Integer)
    count_7 = db.Column(db.Integer)

class Ping1(db.Model):
    __tablename__ = 'ping1'
    id = db.Column(db.Integer, primary_key=True)
    province = db.Column(db.String(20))
    count = db.Column(db.Integer)
    count_7 = db.Column(db.Integer)

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
    url_status = db.relationship('Info_be', back_populates='url_info')
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
    url_info = db.relationship('Status_be', uselist=False, back_populates='url_status')


class Ping2(db.Model):
    __tablename__ = 'ping2'
    province = db.Column(db.String(20), primary_key=True)
    count_7 = db.Column(db.Integer)
    #count_7 = db.Column(db.Integer)


class Pro(db.Model):
    __tablename__ = 'pro'
    id = db.Column(db.Integer, primary_key=True)
    unit_name = db.Column(db.String(500))
    alert = db.Column(db.String(500))


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Base.metadata.create_all(engine)
