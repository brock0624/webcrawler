# -*- coding:utf-8 -*-
# 创建连接相关
from sqlalchemy import create_engine

# 和 sqlapi 交互，执行转换后的 sql 语句，用于创建基类
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker

# 创建连接对象，并使用 pymsql 引擎
conn_str = "mysql+pymysql://{user}:{pwd}@{host}:3306/{db_name}?charset=utf8"
connect_info = conn_str.format(user='test',
                               pwd='test123',
                               db_name='webcrawler',
                               host='zero.brock.fun')

engine = create_engine(connect_info,
                       max_overflow=5,
                       pool_size=5,
                       pool_timeout=30,
                       pool_recycle=-1
                       )

# 创建基类
Base = declarative_base()
Session = sessionmaker(bind=engine)


def init_db():
    """创建所有定义的表到数据库中"""
    Base.metadata.create_all(engine)


def drop_db():
    """从数据库中删除所有定义的表"""
    Base.metadata.drop_all(engine)


class JdItems(Base):
    __tablename__ = 'jd_items'
    id = Column(Integer, primary_key=True, comment="主键id")
    good_url = Column(String(128), comment="商品链接")
    good_name = Column(String(128), comment="商品名称")
    good_price = Column(String(20), comment="商品价格")
    good_commit = Column(String(20), comment="评价人数")
    good_sign = Column(String(64), comment="促销方式")
    good_sign_date = Column(String(64), comment="促销时间")
