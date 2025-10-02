from sqlalchemy import create_engine

from bt4 import GlobalProperties
from bt4.utils.python_utils import SingletonInstance
from bt4.utils.mylog import init_log
log = init_log()

from sqlalchemy.orm import (
    DeclarativeMeta,
    declarative_base,
    scoped_session,
    sessionmaker,
)

Base: DeclarativeMeta = declarative_base()

class DataBaseError :
    pass


class PostgreSQLMgr(SingletonInstance) :
    def __init__(self) :

        PROJECT_NAME: str = GlobalProperties.PROJECT_NAME

        DATABASE_USERNAME: str = GlobalProperties.DATABASE_USERNAME
        DATABASE_PASSWORD: str = GlobalProperties.DATABASE_PASSWORD
        # DATABASE_USERNAME: str = "ssel"
        # DATABASE_PASSWORD: str = "dusrntlf512"
        DATABASE_PORT: str = GlobalProperties.DATABASE_PORT
        DATABASE_NAME: str = GlobalProperties.DATABASE_NAME
        DATABASE_URI: str = GlobalProperties.DATABASE_URI

        DATABASE_SYNC_URL: str = (
            f"postgresql+psycopg2://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_URI}:{DATABASE_PORT}/{DATABASE_NAME}"
        )
        log.info(f"connecting to postgresql url: {DATABASE_SYNC_URL}")
        ECHO_SQL: bool = False  # SQL 로깅
        POOL_SIZE: int = 3          # 10 - default
        MAX_OVERFLOW: int = 1       # 5 - default
        POOL_RECYCLE: int = 1800    # 3600 - default
        POOL_TIMEOUT: int = 10      # 30 - default

        self.sync_host = DATABASE_SYNC_URL
        self.sync_engine_kwargs = {
            "echo"         : ECHO_SQL,
            "pool_size"    : POOL_SIZE,
            "max_overflow" : MAX_OVERFLOW,
            "pool_recycle" : POOL_RECYCLE,
            "pool_timeout" : POOL_TIMEOUT,
        }
        #############################################################
        self.__sync_engine__ = create_engine(self.sync_host, **self.sync_engine_kwargs)
        self.__sync_sessionmaker__ = sessionmaker(autocommit = False, bind = self.__sync_engine__)

        # Base.metadata.drop_all(self.__sync_engine__)
        Base.metadata.create_all(self.__sync_engine__)

    def close_sync(self) :
        if self.__sync_engine__ is None :
            raise DataBaseError("DatabaseSessionManager is not initialized")
        self.__sync_engine__.dispose()
        self.__sync_engine__ = None
        self.__sync_sessionmaker__ = None

    def session(self) :
        if self.__sync_sessionmaker__ is None :
            raise DataBaseError("DatabaseSessionManager is not initialized")

        # return scoped_session(self.__sync_sessionmaker__)()
        return self.__sync_sessionmaker__()



