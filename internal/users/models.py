import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, UniqueConstraint, Index, func
from sqlalchemy import select

import sys, os
import importlib
importlib.reload(sys)

HERE = os.path.abspath(__file__)
HOME_DIR = os.path.split(os.path.split(HERE)[0])[0]
os.sys.path.append(HOME_DIR)
os.sys.path.append(os.path.split(HOME_DIR)[0])

from pkg.mysql.database import Base

STRFTIME_FORMAT = "%Y-%m-%d %H:%M:%S"
STRFDATE_FORMAT = "%Y-%m-%d"

# 基础数据类
class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    create_user = Column(String(64), default="sys", comment="创建用户")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    last_modified_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="最后修改时间")
    last_modified_user = Column(String(64), default="sys", comment="最后变更人")


class User(BaseModel):
    __tablename__ = "user"

    username = Column(String(64), comment="用户名")
    cnname = Column(String(32), comment="中文名")
    avatar_icon = Column(String(256), comment="头像地址")
    email = Column(String(64), comment="邮箱地址")
    mobile = Column(String(16), comment="电话号码")
    feishu_user_id = Column(String(32), comment="飞书user_id")
    feishu_user_union_id = Column(String(64), comment="飞书union_id")
    is_resigned = Column(Boolean, default=False, comment="是否离职")

    @property
    def to_dict(self):
        return {
                "id": self.id,
                "username": self.username,
                "cnname": self.cnname,
                "avatar_icon": self.avatar_icon,
                "email": self.email,
                "mobile": self.mobile,
                "feishu_user_id": self.feishu_user_id,
                "feishu_user_union_id": self.feishu_user_union_id,
                "is_resigned": self.is_resigned,
                "create_user": self.create_user,
                "create_time": self.create_time.strftime(STRFTIME_FORMAT),
                "last_modified_time": self.last_modified_time.strftime(STRFTIME_FORMAT), 
                "last_modified_user": self.last_modified_user
            }

    @property
    def to_api(self):
        return {
                "username": self.username,
                "cnname": self.cnname,
                "avatar_icon": self.avatar_icon,
                "email": self.email,
                "feishu_user_id": self.feishu_user_id,
                "feishu_user_union_id": self.feishu_user_union_id,
                "is_resigned": self.is_resigned,
                "create_time": self.create_time.strftime(STRFTIME_FORMAT),
                "last_modified_time": self.last_modified_time.strftime(STRFTIME_FORMAT)
            }

    
class App(BaseModel):
    __tablename__ = "app"

    name = Column(String(32), unique=True, comment="应用名称")
    union_id = Column(String(64), unique=True, comment="唯一标识")
    owner = Column(String(32), comment="负责人")
    desc = Column(String(128), comment="备注/说明")
    is_active = Column(Boolean, default=True, comment="是否活跃")

    @property
    def to_dict(self):
        return {
                "id": self.id,
                "name": self.name,
                "union_id": self.union_id,
                "owner": self.owner,
                "desc": self.desc,
                "is_active": self.is_active,
                "create_user": self.create_user,
                "create_time": self.create_time.strftime(STRFTIME_FORMAT),
                "last_modified_time": self.last_modified_time.strftime(STRFTIME_FORMAT), 
                "last_modified_user": self.last_modified_user
            }


class Navigation(BaseModel):
    __tablename__ = "navigation"

    app_union_id = Column(String(64), comment="应用唯一标识")
    nav_id = Column(String(32), unique=True, comment="导航id")
    nav_parent_id = Column(String(32), comment="父id")
    name = Column(String(32), comment="名称")
    route = Column(String(32), unique=True, comment="路由名称")
    icon = Column(String(32), comment="图标", default="el-icon-loading")
    desc = Column(String(1024), nullable=True, comment=u"描述")
    order = Column(Integer, comment=u"排序", default=0) 

    @property
    def to_dict(self):
        return {
                "id": self.id,
                "app_union_id": self.app_union_id,
                "nav_id": self.nav_id,
                "nav_parent_id": self.nav_parent_id,
                "name": self.name,
                "route": self.route,
                "icon": self.icon,
                "desc": self.desc,
                "order": self.order,   
                "create_user": self.create_user,
                "create_time": self.create_time.strftime(STRFTIME_FORMAT),
                "last_modified_time": self.last_modified_time.strftime(STRFTIME_FORMAT), 
                "last_modified_user": self.last_modified_user
            }
    
    @property
    def to_navdata(self):
        childs = [i.to_dict for i in select(Navigation).where(Navigation.nav_parent_id==self.nav_id)]
        if childs:
            return {"entity": self.to_dict, "childs": childs}
        else:
            return {"entity": self.to_dict}
                

def init_db():
    from pkg.mysql.database import engine
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    print("ok")
    init_db()
