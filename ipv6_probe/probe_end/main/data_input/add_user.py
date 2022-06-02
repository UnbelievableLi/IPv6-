from models import User, Session


def insert_data():
    session = Session()

    new_user = User(username='probe', password='probingipv6')
    session.add(new_user)
    session.commit()
    session.close()


if __name__ == '__main__':
    insert_data()
