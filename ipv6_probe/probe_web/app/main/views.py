from flask import render_template, url_for, redirect, flash, current_app, request,session
from . import main
from ..models import Status, Info, Hist, School
from .forms import SearchForm,dropdownlist
from flask_login import login_required
from sqlalchemy import or_
from flask import make_response, send_file, send_from_directory
import time
import pandas as pd
import os, sys, stat
import openpyxl as xl



@main.route('/list', methods=['GET', 'POST'])
@login_required
def index():
    all_info = []
    province={}                                   ## 获取各省的url个数
    all_province={}                               ## 获取当月各省ipv6通的数量
    page = request.args.get('page', 1, type=int)
    form1 = SearchForm()
    form = dropdownlist()
    if form.submit.data and form.validate():
        kw = dict(form.word.choices).get(form.word.data)
        #kw = form.word.data
        return redirect(url_for('main.search',kw=dict(form.word.choices).get(form.word.data)))
    elif form1.submit1.data and form1.validate():
        kt = form1.keyword.data
        return redirect(url_for('main.search1', kw=kt))
    else:
        pagination = Status.query.paginate(page, per_page=5, error_out=False)
        result = pagination.items
        Count = Info.query.count()
        Count1 = Status.query.filter(or_((Status.http2_v6=='Y'),(Status.http_v6=='Y'),(Status.https_v6=='Y'))).count()


            
        Count_pro=Hist.query.all()
        for t in Count_pro:
            province[t.province] = Info.query.filter(Info.province.like(t.province)).count()                                              ## 获取当月各省的url的数量
            localtime = time.localtime(time.time())
            if localtime.tm_mon == 1:
                all_province[t.province]=t.january
            if localtime.tm_mon == 2:
                all_province[t.province]=t.february
            if localtime.tm_mon == 3:
                all_province[t.province]=t.march
            if localtime.tm_mon == 4:
                all_province[t.province]=t.april
            if localtime.tm_mon == 5:
                all_province[t.province]=t.may
            if localtime.tm_mon == 6:
                all_province[t.province]=t.june
            if localtime.tm_mon == 7:
                all_province[t.province]=t.july
            if localtime.tm_mon == 8:
                all_province[t.province]=t.august
            if localtime.tm_mon == 9:
                all_province[t.province]=t.september
            if localtime.tm_mon == 10:
                all_province[t.province]=t.october
            if localtime.tm_mon == 11:
                all_province[t.province]=t.november
            if localtime.tm_mon == 12:
                all_province[t.province]=t.december
    
        for r in result:
            single = [r.url_status.unit, r.url_status.url, r.http_v4, r.https_v4, r.http2_v4,
                    r.http_v6, r.https_v6, r.http2_v6]
            all_info.append(single)

        return render_template('index.html', form=form,form1=form1, content=all_info, pagination=pagination,Count=Count,
                            Count1=Count1,pro=all_province,pro_all=province)



@main.route('/search/<kw>', methods=['GET', 'POST'])
@login_required
def search(kw):
    all_info = []
    page = request.args.get('page', 1, type=int)
    form1 = SearchForm()
    form = dropdownlist()
    #form = dropdownlist()
    #kw = dict(form.word.choices).get(form.word.data)
    if form.submit.data and form.validate():
        return redirect(url_for('main.search', kw=dict(form.word.choices).get(form.word.data)))
    elif form1.submit1.data and form1.validate():
        kt = form1.keyword.data
        return redirect(url_for('main.search1', kw=kt))
    else:
        Count= Info.query.filter(Info.province.like(kw)).count()     ## 省所有url个数
        result1= Hist.query.filter_by(province=kw).first()
        localtime = time.localtime(time.time())
        if localtime.tm_mon == 1:             ## Count0 为当月ipv6通数据
            Count0 = result1.january
        if localtime.tm_mon == 2:
            Count0 = result1.february
        if localtime.tm_mon == 3:
            Count0 = result1.march
        if localtime.tm_mon == 4:
            Count0 = result1.april
        if localtime.tm_mon == 5:
            Count0 = result1.may
        if localtime.tm_mon == 6:
            Count0 = result1.june
        if localtime.tm_mon == 7:
            Count0 = result1.july
        if localtime.tm_mon == 8:
            Count0 = result1.august
        if localtime.tm_mon == 9:
            Count0 = result1.september
        if localtime.tm_mon == 10:
            Count0 = result1.october
        if localtime.tm_mon == 11:
            Count0 = result1.november
        if localtime.tm_mon == 12:
            Count0 = result1.december

        Count1=result1.january
        Count2=result1.february
        Count3=result1.march
        Count4=result1.april
        Count5=result1.may
        Count6=result1.june
        Count7=result1.july
        Count8=result1.august
        Count9=result1.september
        Count10=result1.october
        Count11=result1.november
        Count12=result1.december

        Count_not=Count-Count0    #非v6数
    #result1= Info.query.filter(Info.province.like(kw))
        pagination = Info.query.filter(Info.url.like(kw) | Info.province.like(kw)).paginate(
            page, per_page=5, error_out=False)
        result = pagination.items
    #Count1=0

    #for r in result1:
    #   if ((r.url_info.http_v6=='Y') | (r.url_info.https_v6=='Y') | (r.url_info.http2_v6=='Y')):
     #       Count1=Count1+1
        for r in result:
        #   if len(all_info)<20:
            single = [r.unit, r.url, r.url_info.http_v4, r.url_info.https_v4, r.url_info.http2_v4, r.url_info.http_v6,
                    r.url_info.https_v6, r.url_info.http2_v6]
            all_info.append(single)
          #   else:
         #       break
        #if ((r.url_info.http_v6=='Y') | (r.url_info.https_v6=='Y') | (r.url_info.http2_v6=='Y')):
         #   Count1=Count1+1
        return render_template('search.html', form=form,form1=form1, content=all_info, pagination=pagination,kw=kw,Count=Count,Count0=Count0,Count1=Count1,Count2=Count2,
                            Count3=Count3,Count4=Count4,Count5=Count5,Count6=Count6,Count7=Count7,Count8=Count8,Count9=Count9,Count10=Count10,Count_not=Count_not,
                            Count11=Count11,Count12=Count12)

@main.route('/search1/<kw>', methods=['GET', 'POST'])
@login_required
def search1(kw):
    all_info = []
    page = request.args.get('page', 1, type=int)
    form = dropdownlist()
    form1 = SearchForm()
    #kw = dict(form.word.choices).get(form.word.data)
    if form.submit.data and form.validate():
        kw = dict(form.word.choices).get(form.word.data)
        #kw = form.word.data
        return redirect(url_for('main.search',kw=dict(form.word.choices).get(form.word.data)))
    elif form1.submit1.data and form1.validate():
        kt = form1.keyword.data
        return redirect(url_for('main.search1', kw=kt))
    else:
         Count= Info.query.filter_by(unit=kw).count()
         result1= School.query.filter_by(school=kw).first()
         if result1:
              Count1 = result1.count    ## 当月各学校ipv6数量                 2019/11/12， 学校的历史数据，先不变   之后再改动

              Count_not = Count - Count1       ## 未通ipv6的数量
    #result1= Info.query.filter(Info.province.like(kw))
              pagination = Info.query.filter_by(unit=kw).paginate(
              page, per_page=5, error_out=False)
              result = pagination.items
    #Count1=0

    #for r in result1:
    #   if ((r.url_info.http_v6=='Y') | (r.url_info.https_v6=='Y') | (r.url_info.http2_v6=='Y')):
     #       Count1=Count1+1
              for r in result:

                single = [r.unit, r.url, r.url_info.http_v4, r.url_info.https_v4, r.url_info.http2_v4, r.url_info.http_v6,
                        r.url_info.https_v6, r.url_info.http2_v6]
                all_info.append(single)

              return render_template('school.html', form=form,form1=form1, content=all_info, pagination=pagination,kw=kw,Count=Count,
                                        Count1=Count1,Count_not=Count_not)
         else:
              return render_template('404.html')


              
@main.route('/download', methods=['GET'])
@login_required
def download():
    #name=['单位','URL','http/IPv4','https/IPv4','http2/IPv4','http/Ipv6','https/IPv6','http2/IPv6']
    #alien= 'edfdsfsd'
    #test=pd.DataFrame(columns=name,data=all_info)
    #test.to_excel('result.xlsx',encoding='utf-8-sig')
    #response = make_response(alien)
    #response.headers["Content-Disposition"] = "attachment; filename=myfilename.csv"


    response = make_response(send_file("../../result.csv"))
    response.headers["Content-Disposition"] = "attachment; filename=university.csv;"
    return response

