from models import Status_be, Info_be, Session
import csv



def insert_data():
    f2 = open('xindomain-37.CSV', 'r', encoding='utf-8-sig')
    c2 = csv.reader(f2)
    next(c2, None)
    l2 = list(c2)
    # print(l1[:100])
    # print(l2[:100])
    # print(l3[:100])

    session = Session()
    for url in l2:
        flag = 0
        new_info = Info_be(id=url[0].strip(), url=url[1].strip(), description=url[2].strip(),
                        unit_name=url[3].strip(), unit_code=url[4].strip(), title=url[5].strip(),
                        up_unit_code=url[6].strip(), up_unit_code1=url[7].strip(),
                           up_unit_code2=url[8].strip(), up_unit_code3=url[9].strip())
        session.add(new_info)
    #     if url[1].strip()[:7] == 'http://':
    #         u = url[1].strip()[7:].lower()
    #     elif url[1].strip()[:8] == 'https://':
    #         u = url[1].strip()[8:].lower()
    #     else:
    #         u = url[1].strip().lower()
    #
    #     for _u in l1:
    #         if _u[0].strip() == u:
    #             # print(url[1])
    #             # print(_u[0])
    #             new_status = Status(http_v4=_u[1].strip(), https_v4=_u[2].strip(), http2_v4=_u[3].strip(),
    #                                 http_v6=_u[4].strip(), https_v6=_u[5].strip(), http2_v6=_u[6].strip())
    #             flag = 1
    #             break
    #
    #     if flag == 0:
    #         raise IndexError
    #
    #     new_info.url_info = new_status
    #
    #     session.add(new_status)
    for i in range(1, 34939):
        new_status = Status_be(url_id=i)
        session.add(new_status)


    #     flag = 0
    #
    # for ip in l3:
    #     ips = ip[1].split('-')
    #     if len(ips) == 1:
    #         new_ip = IP(unit=ip[0].strip(), address_begin=ips[0].strip())
    #     elif len(ips) == 2:
    #         new_ip = IP(unit=ip[0].strip(), address_begin=ips[0].strip(), address_end=ips[1].strip())
    #     session.add(new_ip)

    session.commit()

    session.close()
    f2.close()


if __name__ == '__main__':
    insert_data()
