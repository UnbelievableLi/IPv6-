from flask import render_template, url_for, redirect, flash, current_app, request,session
from . import ji
from ..models import Status, Info,Ping,Ping1,School,Status_be,Info_be,Ping2,Pro
from .forms import SearchForm,dropdownlist
from flask_login import login_required
from sqlalchemy import or_


@ji.route('/listji', methods=['GET', 'POST'])
@login_required
def indexji():
    all_info = []
    all_province={}
    page = request.args.get('page', 1, type=int)
    # form1 = SearchForm()
    form = dropdownlist()
    if form.submit.data and form.validate():
        kw = dict(form.word.choices).get(form.word.data)
        #kw = form.word.data
        return redirect(url_for('ji.searchji',kw=dict(form.word.choices).get(form.word.data)))
    # elif form1.submit1.data and form1.validate():
    #     kt = form1.keyword.data
    #     return redirect(url_for('ji.search1ji', kw=kt))
    else:
         pagination = Status_be.query.paginate(page, per_page=current_app.config['NUMBER_PER_PAGE'], error_out=False)
         result = pagination.items
         Count = Info_be.query.count()
         Count1 = Status_be.query.filter(or_((Status_be.http2_v6=='Y'),(Status_be.http_v6=='Y'),(Status_be.https_v6=='Y'))).count()
         Cout_7=Ping2.query.all()
         for t in Cout_7:
             all_province[t.province]=t.count_7
         #print(all_province)
         for r in result:
             #if len(all_info) < 20:
                single = [r.url_status.unit_name, r.url_status.url, r.http_v4, r.https_v4, r.http2_v4,
                       r.http_v6, r.https_v6, r.http2_v6]
                all_info.append(single)
             #else:
              #  break
         return render_template('indexji.html', form=form, content=all_info, pagination=pagination,Count=Count,
                                Count1=Count1,pro=all_province)


@ji.route('/searchji/<kw>', methods=['GET', 'POST'])
@login_required
def searchji(kw):
    all_info = []
    page = request.args.get('page', 1, type=int)
    # form1 = SearchForm()
    form = dropdownlist()
    #form = dropdownlist()
    #kw = dict(form.word.choices).get(form.word.data)
    if form.submit.data and form.validate():
        return redirect(url_for('ji.searchji', kw=dict(form.word.choices).get(form.word.data)))
    # elif form1.submit1.data and form1.validate():
    #     kt = form1.keyword.data
    #     return redirect(url_for('ji.search1ji', kw=kt))
    else:
         f= Pro.query.filter(Pro.unit_name.like(kw)).first()
         print(f)
         kv=f.alert
         Count= Info_be.query.filter(or_((Info_be.up_unit_code==kv),(Info_be.up_unit_code1==kv),
                                         (Info_be.up_unit_code2==kv),(Info_be.up_unit_code3==kv),(Info_be.unit_code==kv))).count()
         # result1= Ping.query.filter_by(province=kw).first()
         # Count1=result1.count #4月份数据
         y=Ping2.query.filter_by(province=kw).first()
         # Count3=y.count#6月份数据
         Count7=y.count_7#7月份数据
         Count2=Count-Count7
    #result1= Info.query.filter(Info.province.like(kw))
         pagination = Info_be.query.filter(or_((Info_be.up_unit_code==kv),(Info_be.up_unit_code1==kv),
                                         (Info_be.up_unit_code2==kv),(Info_be.up_unit_code3==kv),(Info_be.unit_code==kv))).paginate(
         page, per_page=current_app.config['NUMBER_PER_PAGE'], error_out=False)
         result = pagination.items
    #Count1=0

    #for r in result1:
    #   if ((r.url_info.http_v6=='Y') | (r.url_info.https_v6=='Y') | (r.url_info.http2_v6=='Y')):
     #       Count1=Count1+1
         for r in result:
          #   if len(all_info)<20:
                single = [r.unit_name, r.url, r.url_info.http_v4, r.url_info.https_v4, r.url_info.http2_v4, r.url_info.http_v6,
                        r.url_info.https_v6, r.url_info.http2_v6]
                all_info.append(single)
          #   else:
         #       break
        #if ((r.url_info.http_v6=='Y') | (r.url_info.https_v6=='Y') | (r.url_info.http2_v6=='Y')):
         #   Count1=Count1+1
         return render_template('searchji.html', form=form, content=all_info, pagination=pagination,kw=kw,Count=Count,Count2=Count2,
                                Count7=Count7)


# @ji.route('/search1ji/<kw>', methods=['GET', 'POST'])
# @login_required
# def search1(kw):
#     all_info = []
#     page = request.args.get('page', 1, type=int)
#     form = dropdownlist()
#     form1 = SearchForm()
#     #kw = dict(form.word.choices).get(form.word.data)
#     if form.submit.data and form.validate():
#         kw = dict(form.word.choices).get(form.word.data)
#         #kw = form.word.data
#         return redirect(url_for('main.search',kw=dict(form.word.choices).get(form.word.data)))
#     elif form1.submit1.data and form1.validate():
#         kt = form1.keyword.data
#         return redirect(url_for('main.search1', kw=kt))
#     else:
#          Count= Info.query.filter_by(unit=kw).count()
#          result1= School.query.filter_by(school=kw).first()
#          if result1:
#               Count1=result1.count#6月份
#               Count3 = result1.count#6月份
#               Count7 = result1.count_7  # 7月份数据
#               Count2 = Count - Count7
#     #result1= Info.query.filter(Info.province.like(kw))
#               pagination = Info.query.filter_by(unit=kw).paginate(
#               page, per_page=current_app.config['NUMBER_PER_PAGE'], error_out=False)
#               result = pagination.items
#     #Count1=0
#
#     #for r in result1:
#     #   if ((r.url_info.http_v6=='Y') | (r.url_info.https_v6=='Y') | (r.url_info.http2_v6=='Y')):
#      #       Count1=Count1+1
#               for r in result:
#
#                 single = [r.unit, r.url, r.url_info.http_v4, r.url_info.https_v4, r.url_info.http2_v4, r.url_info.http_v6,
#                         r.url_info.https_v6, r.url_info.http2_v6]
#                 all_info.append(single)
#
#               return render_template('school.html', form=form,form1=form1, content=all_info, pagination=pagination,kw=kw,Count=Count,Count1=Count1,Count2=Count2,
#                                 Count3=Count3, Count7=Count7)
#          else:
#               return render_template('404.html')

