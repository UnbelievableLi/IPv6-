from flask import render_template, url_for, redirect, flash, current_app, request,session
from . import ji
from ..models import Status, Info,School,Status_be,Info_be,Pro,Hist_ele
from .forms import SearchForm,dropdownlist
from flask_login import login_required
from flask import make_response, send_file, send_from_directory
from sqlalchemy import or_
import time
import pandas as pd
import os, sys, stat
import openpyxl as xl

@ji.route('/listji', methods=['GET', 'POST'])
@login_required
def indexji():
    all_info = []
    all_province={}             ## 各个省份通ipv6的数量
    province={}                    ## 各个省份的url数
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
        pagination = Status_be.query.paginate(page, per_page=5, error_out=False)
        result = pagination.items
        Count = Info_be.query.count()   ## url总数
        ## Count1 = Status_be.query.filter(or_((Status_be.http2_v6=='Y'),(Status_be.http_v6=='Y'),(Status_be.https_v6=='Y'))).count()
        ##ipv6通的数量
        Count_pro=Hist_ele.query.all()
        for t in Count_pro:
            f= Pro.query.filter(Pro.unit_name.like(t.province)).first()
            kv=f.alert
            province[t.province] = Info_be.query.filter(or_((Info_be.up_unit_code==kv),(Info_be.up_unit_code1==kv),
                                            (Info_be.up_unit_code2==kv),(Info_be.up_unit_code3==kv),(Info_be.unit_code==kv))).count()                                        ## 获取当月各省的ipv6通的数量
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


        Count1 = 0         ## ipv6的总数
        for val in all_province.values():
            Count1 = Count1 + val


        for r in result:
            single = [r.url_status.unit_name, r.url_status.url, r.http_v4, r.https_v4, r.http2_v4,
                    r.http_v6, r.https_v6, r.http2_v6]
            all_info.append(single)
            #else:
            #  break
        return render_template('indexji.html', form=form, content=all_info, pagination=pagination,Count=Count,
                            Count1=Count1,pro=all_province,pro_all=province)


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
       
        y=Hist_ele.query.filter_by(province=kw).first()
        localtime = time.localtime(time.time())
        if localtime.tm_mon == 1:             ## Count0 为当月ipv6通数据
            Count0 = y.january
        if localtime.tm_mon == 2:
            Count0 = y.february
        if localtime.tm_mon == 3:
            Count0 = y.march
        if localtime.tm_mon == 4:
            Count0 = y.april
        if localtime.tm_mon == 5:
            Count0 = y.may
        if localtime.tm_mon == 6:
            Count0 = y.june
        if localtime.tm_mon == 7:
            Count0 = y.july
        if localtime.tm_mon == 8:
            Count0 = y.august
        if localtime.tm_mon == 9:
            Count0 = y.september
        if localtime.tm_mon == 10:
            Count0 = y.october
        if localtime.tm_mon == 11:
            Count0 = y.november
        if localtime.tm_mon == 12:
            Count0 = y.december
        Count1=y.january
        Count2=y.february
        Count3=y.march
        Count4=y.april
        Count5=y.may
        Count6=y.june
        Count7=y.july
        Count8=y.august
        Count9=y.september
        Count10=y.october
        Count11=y.november
        Count12=y.december

        Count_not=Count-Count0    #非v6数
    #result1= Info.query.filter(Info.province.like(kw))
        pagination = Info_be.query.filter(or_((Info_be.up_unit_code==kv),(Info_be.up_unit_code1==kv),
                                        (Info_be.up_unit_code2==kv),(Info_be.up_unit_code3==kv),(Info_be.unit_code==kv))).paginate(
        page, per_page=5, error_out=False)
        result = pagination.items
    #Count1=0

    #for r in result1:
    #   if ((r.url_info.http_v6=='Y') | (r.url_info.https_v6=='Y') | (r.url_info.http2_v6=='Y')):
     #       Count1=Count1+1
        for r in result:
        #   if len(all_info)<20:
            single = [r.unit_name, r.url, r.url_info_be.http_v4, r.url_info_be.https_v4, r.url_info_be.http2_v4, r.url_info_be.http_v6,
                    r.url_info_be.https_v6, r.url_info_be.http2_v6]
            all_info.append(single)
        #   else:
        #       break
    #if ((r.url_info.http_v6=='Y') | (r.url_info.https_v6=='Y') | (r.url_info.http2_v6=='Y')):
        #   Count1=Count1+1
        return render_template('searchji.html', form=form, content=all_info, pagination=pagination,kw=kw,Count0=Count0,Count1=Count1,Count2=Count2,
                            Count3=Count3,Count4=Count4,Count5=Count5,Count6=Count6,Count7=Count7,Count8=Count8,Count9=Count9,Count10=Count10,Count11=Count11,
                            Count12=Count12,Count_not=Count_not)

@ji.route('/indexji/downloadbe', methods=['GET', 'POST'])
@login_required
def downloadbe():
    
    response = make_response(send_file("../../result_be.csv"))
    response.headers["Content-Disposition"] = "attachment; filename=Elementary_education.csv;"
    return response
