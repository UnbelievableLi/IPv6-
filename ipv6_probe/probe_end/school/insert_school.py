from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:159357@localhost/ipv6probe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class School(db.Model):
    __tablename__ = 'school'
    id = db.Column(db.Integer, primary_key=True)
    school = db.Column(db.String(100))
    count = db.Column(db.Integer)


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    db.session.commit()
    sql = "insert into school (school) select distinct unit from info"
    db.session.execute(sql)
    db.session.commit()
    app.run(debug=True)
