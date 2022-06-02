from models import Status_be, Info_be, Session,Pro
import csv



def insert_data():
    f2 = open('xinunit-25.CSV', 'r', encoding='utf-8-sig')
    c2 = csv.reader(f2)
    next(c2, None)
    l2 = list(c2)
    # print(l1[:100])
    # print(l2[:100])
    # print(l3[:100])

    session = Session()
    for url in l2:
        flag = 0
        new_info = Pro(id=url[0].strip(), unit_name=url[1].strip(), alert=url[2].strip())
        session.add(new_info)
  

    session.commit()

    session.close()
    f2.close()


if __name__ == '__main__':
    insert_data()
