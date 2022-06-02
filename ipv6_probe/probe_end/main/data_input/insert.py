from models import Status, Info, IP, Session
import csv


def insert_data():
    f1 = open('result.csv', 'r', encoding='utf-8-sig')
    f2 = open('info.csv', 'r', encoding='utf-8-sig')
    f3 = open('ip.csv', 'r', encoding='utf-8-sig')
    c1 = csv.reader(f1)
    c2 = csv.reader(f2)
    c3 = csv.reader(f3)
    l1 = list(c1)
    l2 = list(c2)
    l3 = list(c3)

    # print(l1[:100])
    # print(l2[:100])
    # print(l3[:100])

    session = Session()

    for url in l2:
        flag = 0
        new_info = Info(unit=url[0].strip(), url=url[1].strip(), description=url[2].strip(),
                        open_status=url[3].strip(), remark=url[4].strip())

        if url[1].strip()[:7] == 'http://':
            u = url[1].strip()[7:].lower()
        elif url[1].strip()[:8] == 'https://':
            u = url[1].strip()[8:].lower()
        else:
            u = url[1].strip().lower()

        for _u in l1:
            if _u[0].strip() == u:
                # print(url[1])
                # print(_u[0])
                new_status = Status(http_v4=_u[1].strip(), https_v4=_u[2].strip(), http2_v4=_u[3].strip(),
                                    http_v6=_u[4].strip(), https_v6=_u[5].strip(), http2_v6=_u[6].strip())
                flag = 1
                break

        if flag == 0:
            raise IndexError

        new_info.url_info = new_status

        session.add(new_status)
        session.add(new_info)
        flag = 0

    for ip in l3:
        ips = ip[1].split('-')
        if len(ips) == 1:
            new_ip = IP(unit=ip[0].strip(), address_begin=ips[0].strip())
        elif len(ips) == 2:
            new_ip = IP(unit=ip[0].strip(), address_begin=ips[0].strip(), address_end=ips[1].strip())
        session.add(new_ip)

    session.commit()

    session.close()
    f1.close()
    f2.close()
    f3.close()


if __name__ == '__main__':
    insert_data()

