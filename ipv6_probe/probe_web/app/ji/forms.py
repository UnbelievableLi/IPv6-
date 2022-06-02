from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField
from wtforms.validators import DataRequired, Length


class SearchForm(FlaskForm):
    keyword = StringField('学校查询', validators=[DataRequired(), Length(1, 64)])
    submit1 = SubmitField('查询')
class dropdownlist(FlaskForm):
    word = SelectField('省份查询',validators=[DataRequired()], choices=[('1', '江苏省'),('2', '陕西省'),('3', '上海市'),('4', '黑龙江省'),
                                                                      ('5', '北京市'),('6', '天津市'),('7', '重庆市'),('8', '河北省'),('9', '山西省')
    ,('10', '辽宁省'),('11', '吉林省'),('12', '浙江省'),('13', '安徽省'),('14', '福建省'),('15', '江西省'),('16', '山东省')
    ,('17', '河南省'),('18', '湖北省'),('19', '湖南省'),('20', '广东省'),('21', '海南省'),('22', '四川省'),('23', '贵州省')
    ,('24', '云南省'),('25', '青海省'),('26', '甘肃省'),('27', '台湾省'),('28', '内蒙古自治区'),('29', '广西壮族自治区'),('30', '西藏自治区'),
                                                                      ('31', '宁夏回族自治区'),('32', '新疆维吾尔自治区')
                                                                      ,('33', '香港特别行政区'),('34', '澳门特别行政区')])
    submit = SubmitField('查询')