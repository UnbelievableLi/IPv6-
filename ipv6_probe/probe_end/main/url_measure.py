import re
import pycurl
import pickle
import certifi
import threading
import logging
import requests
import socket1
from io import BytesIO
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:159357@localhost/ipv6probe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


final_result = {}
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler('output.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


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


def test_website(url, ip_ver=4, http='http'):
    status = 'N'  # 最终结果
    errs = ''

    def debug_func(debug_type, debug_msg):
        nonlocal status
        if debug_type == 1 or debug_type == 0:
            msg = debug_msg.decode('utf-8', errors='ignore').strip()
            if http == 'http2' and msg == 'HTTP/2 200':
                status = 'Y'
            if http != 'http2' and re.match(r'HTTP/1\.[0|1]\s200\sOK', msg):
                status = 'Y'
            # print(debug_type, msg)

    c = pycurl.Curl()
    ua = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.A.B.C Safari/525.13'
    buffer = BytesIO()
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(pycurl.CAINFO, certifi.where())
    c.setopt(c.USERAGENT, ua)
    c.setopt(c.MAXREDIRS, 5)
    c.setopt(c.FOLLOWLOCATION, True)  # 跟踪爬取重定向页面
    c.setopt(c.CONNECTTIMEOUT, 15)
    c.setopt(c.TIMEOUT, 5)
    c.setopt(pycurl.VERBOSE,True)
    c.setopt(pycurl.DEBUGFUNCTION, debug_func)

    if ip_ver == 4:
        c.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V4)
    elif ip_ver == 6:
        c.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V6)
    else:
        raise ValueError

    try:
        if http == 'http':
            c.setopt(c.URL, 'http://' + url)
        elif http == 'https':
            c.setopt(c.URL, 'https://' + url)
#        elif http == 'http2':
#            c.setopt(c.URL, 'http2://' + url)
#            c.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_2_0)
        else:
            raise ValueError
    except UnicodeEncodeError:
        errs = 'url unicode encode error'
        return status, errs

    try:
        c.perform()
    except pycurl.error as e:
        if e.args[0] == 6:
            errs = 'Error: cannot resolve'
            if ((ip_ver == 4) & (http == 'http')):
                status = request1(url)
                if status == 'Y':
                    errs = ''
        elif e.args[0] == 7:
            errs = 'Error: cannot connect'
        elif e.args[0] == 28:
            errs = 'Error: timeout'
        elif e.args[0] == 35:
            errs = 'Error: ssl connect error'
        elif e.args[0] == 60:
            errs = "Error: peer's certificate or fingerprint wasn't verified fine"
        else:
            errs = 'Error code:' + str(e.args[0])
    if ((ip_ver == 4)&(http == 'http')&(status=='N')):
        status = request1(url)
        if status=='Y':
            errs=''
    if ((ip_ver == 6) & (http == 'http') & (status == 'N')&(errs!='Error: cannot resolve')):
        status_code, headers, body = socket1.get(url)
        status=status_code
    if ((ip_ver == 6) & (http == 'https') & (status == 'N')&(errs!='Error: cannot resolve')):
        t_url = str('https://' + url)
        status_code, headers, body = socket1.get(t_url)
        status=status_code
    return status, errs

def request1(url):
    i = 80
    t_url = str('http://' + url)
    try:
        proxies = {'http': t_url + ':' + str(i)}
        ua = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.A.B.C Safari/525.13'
        headers = {'User-Agent': ua}
        r = requests.get(t_url, timeout=3, proxies=proxies, headers=headers)
        if r.status_code == requests.codes.ok:
            status ='Y'
            # print(r.status_code)
        else:
            status = 'N'
            r.raise_for_status()
    except:
        status = 'N'
    return status

def test_url(url):
    h_4 = test_website(url, 4, 'http')
    if h_4[1] != 'Error: cannot resolve':
        hs_4 = test_website(url, 4, 'https')
      #  h2_4 = test_website(url, 4, 'http2')
        h2_4 = ('N', 'Error: cannot resolve')
    else:
        hs_4 = ('N', 'Error: cannot resolve')
        h2_4 = ('N', 'Error: cannot resolve')

    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
        # 如果是ipv4地址就不测试ipv6
        h_6 = test_website(url, 6, 'http')
        if h_6[1] != 'Error: cannot resolve':
            hs_6 = test_website(url, 6, 'https')
        #    h2_6 = test_website(url, 6, 'http2')
            h2_6 = ('N', 'Error: cannot resolve')
        else:
            hs_6 = ('N', 'Error: cannot resolve')
            h2_6 = ('N', 'Error: cannot resolve')
    else:
        h_6 = ('N', '')
        hs_6 = ('N', '')
        h2_6 = ('N', '')

    #print(h_4, hs_4, h2_4, h_6, hs_6, h2_6)

    return h_4, hs_4, h2_4, h_6, hs_6, h2_6

count = 0
def run(url_sublist):
    global count
    global logger
    global final_result
    for url in url_sublist:
        logger.info('begin processing: %s', url)
        t_url = url.strip()
        if t_url[:7] == 'http://':
            t_url = t_url[7:]
        if t_url[:8] == 'https://':
            t_url = t_url[8:]
        if t_url[-1] == '/':
            t_url = t_url[:-1]
        print(t_url)
        result = test_url(t_url)
        final_result[url] = result
        logger.info('end processing: %s', url)
        count = count + 1
        print(count)


def multi_thread():
    with open('all_urls.pkl', 'rb') as f:
        urls = pickle.load(f)
        # print(len(urls))
        # 92882
    thread_list = []
    for i in range(3097):
        if i != 3096:
            th = threading.Thread(target=run, args=(urls[i*30:(i+1)*30],))
            # th = threading.Thread(target=run, args=(urls[i * 300:i * 300+1],))
        else:
            # th = threading.Thread(target=run, args=(urls[90000:90001],))
            th = threading.Thread(target=run, args=(urls[92880:],))
        # test
      #  th = threading.Thread(target=run, args=(urls[i * 5:(i + 1) * 5],))

        thread_list.append(th)
        th.start()

    for th in thread_list:
        th.join()


def read_url():
    all_info = Info.query.all()

    all_urls = []

    for i, s in enumerate(all_info):
        all_urls.append(s.url)

    with open('all_urls.pkl', 'wb') as f:
        pickle.dump(all_urls, f)


def write_result():
    global final_result
    k = ['http_v4', 'https_v4', 'http2_v4', 'http_v6', 'https_v6', 'http2_v6']

    for url, res in final_result.items():
        curr = {}
        for i, r in enumerate(res):
            if r[0] == 'N' and r[1] != '':
                curr[k[i]] = r[1]
            else:
                curr[k[i]] = r[0]
        s = Status.query.join(Info).filter(Info.url == url).all()
        if len(s) != 1:
            logger.info('find url more than 1')
            logger.info('url:', url)
            logger.info('numbers:', len(s))
        sel = s[0]
        sel.http_v4 = curr['http_v4']
        sel.https_v4 = curr['https_v4']
        sel.http2_v4 = curr['http2_v4']
        sel.http_v6 = curr['http_v6']
        sel.https_v6 = curr['https_v6']
        sel.http2_v6 = curr['http2_v6']
        db.session.commit()

    


def main():
    try:
        read_url()
        multi_thread()
        write_result()

    except Exception:
        logger.error('Run error: ', exc_info=True)


if __name__ == '__main__':
    main()
