import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

HERE = os.path.abspath(__file__)
HOME_DIR = os.path.split(os.path.split(HERE)[0])[0]
os.sys.path.append(HOME_DIR)

from apollo.apollo_conf import *

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8mb4".format(user=mysql_db_user, passwd=mysql_db_passwd, host=mysql_db_host, port=mysql_db_port, db_name=mysql_db_name)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    max_overflow = 10,
    pool_size = 20,
    pool_timeout = 30,
    pool_recycle = 3600,
    pool_pre_ping=True
)

Base = declarative_base()
