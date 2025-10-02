import unittest
from sqlalchemy import select, update

from bt4.model.postgresql_mgr import PostgreSQLMgr
from spiketesting._09_postgre_sqlalchemy2.model import Base, User, Address


## http://localhost:8090/
class MyTestCase(unittest.TestCase) :
    def setUp(self) -> None:
        with PostgreSQLMgr.instance().session() as session:
            Base.metadata.drop_all(PostgreSQLMgr.instance().__sync_engine__)
            Base.metadata.create_all(PostgreSQLMgr.instance().__sync_engine__)

    def test_sql_alchemy_create_db_insert_data(self) :

        addr_list = []
        addr1 = Address(email_address = "ABC")
        addr2 = Address(email_address = "bbbbb")

        addr_list.append(addr1)
        addr_list.append(addr2)

        addr_list2 = []
        addr21 = Address(email_address = "aaaaaaaaaaaaaaaaaaaaaaa")
        addr22 = Address(email_address = "xxxxxxxxxxxxxxxxxxxxx")

        addr_list2.append(addr21)
        addr_list2.append(addr22)

        attr_values = {
            'name'      : "AAA",
            'fullname'  : "BBB",
            'addresses' : addr_list
        }
        usr = User(**attr_values)

        attr_values = {
            'name'      : "cccc",
            'fullname'  : "ddddd",
            'addresses' : addr_list2
        }
        usr2 = User(**attr_values)


        attr_values = {
            'name'      : "eeee",
            'fullname'  : "fffff",
            'addresses' : addr_list2
        }
        usr3 = User(**attr_values)

        with PostgreSQLMgr.instance().session() as session:
            session.add(usr)
            session.add(usr2)
            session.add(usr3)
            session.commit()

    def test_sql_alchemy_select_data(self) :
        self.test_sql_alchemy_create_db_insert_data()

        with PostgreSQLMgr.instance().session() as session:
            # statement = select(User).filter_by(name = "AAA")
            #
            # # list of ``User`` objects
            # user_obj = session.scalars(statement).all()
            # print(f"{user_obj=}")

            # query for individual columns
            u1 = session.scalar(select(User).filter_by(name = "AAA"))
            print(f"{u1=}")

            # statement = select(User.name, User.fullname).where(User.name == "AAA" )
            statement = select(User.name, User.fullname)
            rows = session.execute(statement).all()
            print(f"{rows=}")

    def test_sql_alchemy_delete(self) :
        self.test_sql_alchemy_create_db_insert_data()

        with PostgreSQLMgr.instance().session() as session :
            u1 = session.scalar(select(User).filter_by(name = "AAA"))
            print(f"{u1=}")
            session.delete(u1)

            statement = select(User.name, User.fullname)
            rows = session.execute(statement).all()
            print(f"{rows=}")

    def test_sql_alchemy_update(self) :
        self.test_sql_alchemy_create_db_insert_data()

        list_of_ojbs = []
        with PostgreSQLMgr.instance().session() as session :
            statement = select(User.name, User.fullname)
            rows = session.execute(statement).all()
            print(f"{rows=}")


            u1 = session.execute(select(User).filter_by(name = "AAA"))
            print(f"{u1=}")
            session.execute(update(User).where(User.name == "AAA").values(fullname = "XXX"))

            statement = select(User.name, User.fullname)
            rows = session.execute(statement).all()
            print(f"{rows=}")


    def test_sql_alchemy_select_address(self) :
        self.test_sql_alchemy_create_db_insert_data()

        with PostgreSQLMgr.instance().session() as session:
            statement = select(Address).join(User).where(User.id == "1")
            rows = session.execute(statement).all()
            print(f"{rows=}")

            u1 = session.scalars(select(Address).join(User).where(User.id == "1")).all()
            print(f"{u1=}")

            u2 = session.scalar(select(Address).join(User).where(User.id == "1"))
            print(f"{u2=}")

            statement = select(Address).join(User).where(User.id == "1")
            rows3 = session.execute(statement).scalars().all()
            print(f"{rows3=}")



if __name__ == '__main__' :
    unittest.main()
