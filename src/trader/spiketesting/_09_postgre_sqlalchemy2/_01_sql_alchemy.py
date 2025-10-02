import unittest
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

from spiketesting._09_postgre_sqlalchemy2.model import Base, User, Address


## http://localhost:8090/
class MyTestCase(unittest.TestCase) :
    def setUp(self) -> None:
        # engine = create_engine("postgresql+psycopg2://bulltrader:qnfxmfpdlej12!@localhost:5432/mydatabase", echo = True)
        self.engine = create_engine("postgresql://bulltrader:qnfxmfpdlej12!@localhost:5432/bt4", echo = True)

        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def test_sql_alchemy_create_db_insert_data(self) :

        addr_list = []
        addr1 = Address(email_address = "ABC")
        addr2 = Address(email_address = "bbbbb")

        addr_list.append(addr1)
        addr_list.append(addr2)

        attr_values = {
            'name'      : "AAA",
            'fullname'  : "BBB",
            'addresses' : addr_list
        }
        usr = User(**attr_values)

        attr_values = {
            'name'      : "cccc",
            'fullname'  : "ddddd",
            'addresses' : addr_list
        }
        usr2 = User(**attr_values)


        attr_values = {
            'name'      : "eeee",
            'fullname'  : "fffff",
            'addresses' : addr_list
        }
        usr3 = User(**attr_values)

        with Session(self.engine) as session :
            session.add(usr)
            session.add(usr2)
            session.add(usr3)
            session.commit()

    def test_sql_alchemy_select_data(self) :
        self.test_sql_alchemy_create_db_insert_data()

        with Session(self.engine) as session :
            # statement = select(User).filter_by(name = "AAA")
            #
            # # list of ``User`` objects
            # user_obj = session.scalars(statement).all()
            # print(f"{user_obj=}")

            # query for individual columns
            u1 = session.scalar(select(User).filter_by(name = "AAA"))
            print(f"{u1=}")

            # statement = select(User.name, User.fullname).where(User.name == "AAA" )
            # rows = session.execute(statement).all()
            # print(f"{rows=}")

    def test_sql_alchemy_delete(self) :
        self.test_sql_alchemy_create_db_insert_data()

        list_of_ojbs = []
        with Session(self.engine) as session :
            u1 = session.scalar(select(User).filter_by(name = "AAA"))
            print(f"{u1=}")
            session.delete(u1)

            statement = select(User.name, User.fullname)
            rows = session.execute(statement).all()
            print(f"{rows=}")

    def test_sql_alchemy_update(self) :
        self.test_sql_alchemy_create_db_insert_data()

        list_of_ojbs = []
        with Session(self.engine) as session :
            u1 = session.execute(select(User).filter_by(name = "AAA"))
            print(f"{u1=}")
            session.execute(update(User).where(User.name == "AAA").values(fullname = "XXX"))

            statement = select(User.name, User.fullname)
            rows = session.execute(statement).all()
            print(f"{rows=}")

if __name__ == '__main__' :
    unittest.main()
