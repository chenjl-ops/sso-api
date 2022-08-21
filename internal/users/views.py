import sys
import os
from fastapi import APIRouter
from fastapi import FastAPI, Query, Cookie
from fastapi import Request
from typing import Union
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from fastapi_utils.tasks import repeat_every

users_router = APIRouter()

HERE = os.path.abspath(__file__)
HOME_DIR = os.path.split(os.path.split(HERE)[0])[0]
os.sys.path.append(HOME_DIR)
os.sys.path.append(os.path.split(HOME_DIR)[0])

from internal.users.models import *
from internal.users.tools import feishu_requests_main, RedisManage

from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from pkg.mysql.database import engine
from pkg.apollo.apollo_conf import *

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

COOKIE_TOKEN_NAME = "xxx_token"
COOKIE_DOMAIN = ".xxx.xxx"

@users_router.get("/", summary="获取User Info", tags=["sso-user"])
def get_user(username: str=None):
    '''
        获取用户信息: 默认获取全量用户数据
        根据用户名获取单个用户数据
    '''
    session = SessionLocal()
    
    if username:
        user = session.query(User).filter_by(username=username).first()
        data = user.to_api
    else:
        users = session.query(User).filter_by()
        data = [i.to_api for i in users]

    return {"code": 200, "data": data}

@users_router.get("/token", summary="用户token校验", tags=["sso-user"])
def check_token(token: str):
    redis = RedisManage(host=redis_host, port=redis_port, db=0, S="sso")
    try:
        user_info_data = redis.get(token)
        return {"code": 200, "data": user_info_data}
    except:
        user_info_data = dict()
        return {"code": 404, "data": user_info_data, "error_message": "user not login success"}


@users_router.get("/feishu/login/callback", summary="飞书登陆回调接口", tags=["sso-user"])
def feishu_login_callback(request: Request, redirect_uri: str, app_name: str, code: str, state: str):
    import uuid
    print("redirect_uri: ", redirect_uri)

    feishu_code_data = {
                "grant_type": "authorization_code",
                "code": code
            }

    url = "https://open.feishu.cn/open-apis/authen/v1/access_token"
    feishu_data = feishu_requests_main("POST", url, feishu_code_data, app_id=feishu_app_id, app_secret=feishu_app_secret)

    print("feishu_data: ", feishu_data)
    if feishu_data.get("code") == 0: #飞书用户校验成功
        token = str(uuid.uuid1()).replace("-","")
        print("token: ", token)
        # token写入redis
        redis = RedisManage(host=redis_host, port=redis_port, db=0, S="sso")
        redis.set(token, feishu_data.get("data"))
        # 设置cookie
        response = RedirectResponse(url=redirect_uri)
        response.set_cookie(COOKIE_TOKEN_NAME, value=token, domain=COOKIE_DOMAIN, expires=60*60*12)
        return response

@users_router.get("/feishu/login", summary="登录跳转接口", tags=["sso-user"])
#def feishu_login(request: Request, redirect_uri: str, app_name: str, jy_token: Union[str, None] = Cookie(None)):
def feishu_login(request: Request, redirect_uri: str, app_name: str):
    import urllib
    from urllib import parse
    redirect_url = base_redirect_url + "?redirect_uri={redirect_uri}&app_name={app_name}".format(redirect_uri=redirect_uri, app_name=app_name)

    # 处理请求url, 保留非必要参数其他query
    request_url = request.url.__str__()
    request_query = parse.parse_qs(parse.urlparse(request_url).query)
    s = "&".join(["%s=%s"%(x, y[0]) for x, y in request_query.items() if x not in ["redirect_uri", "app_name"]])
    
    if s:
        redirect_url = redirect_url + "&" + s
    else:
        redirect_url = redirect_url + s

    redirect_url = urllib.parse.quote(redirect_url, encoding=None, errors=None)
    url = "https://open.feishu.cn/open-apis/authen/v1/index?redirect_uri={REDIRECT_URI}&app_id={APPID}&state={STATE}".format(\
        REDIRECT_URI=redirect_url, \
        APPID=feishu_app_id, \
        STATE="sso-api"\
    )
    return RedirectResponse(url=url) 
    
@users_router.get("/feishu/logout", summary="退出登录", tags=["sso-user"])
def feishu_logout(request: Request, redirect_uri: str, app_name: str, jy_token: Union[str, None] = Cookie(None)):
    response = RedirectResponse(redirect_uri)
    if jy_token: # cookie有相关token 删除token 
        response.delete_cookie(COOKIE_TOKEN_NAME, domain=COOKIE_DOMAIN)
    return response

@repeat_every(seconds=60 * 10)
@users_router.get("/flush_user", summary="刷新用户", tags=["sso-user"])
def flush_feishu_user() -> None:
    import requests

    print("flush feishu user start.....")
    feishu_api_path="/v1/users/all"

    url = "{base_url}{path}?app_id={app_id}&app_secret={app_secret}".format(base_url=feishu_api_url, path=feishu_api_path, app_id=feishu_app_id, app_secret=feishu_app_secret)
    user_data = requests.get(url).json()

    for user in user_data:
        session = SessionLocal()
        user_model = session.query(User).filter_by(feishu_user_id=user.get("user_id", "")).first()

        if user_model: # Update
            user_model.username = user.get("email", "").split("@")[0]
            user_model.cnname = user.get("name", "")
            user_model.avatar_icon = user.get("avatar", dict()).get("avatar_origin", "")
            user_model.email = user.get("email", "")
            user_model.mobile = user.get("mobile", "")
            user_model.feishu_user_id = user.get("user_id", "")
            user_model.feishu_user_union_id = user.get("union_id", "")

            session.commit()
            session.close()
        else: # Insert
            user_model = User(
                            username=user.get("email", "").split("@")[0],
                            cnname = user.get("name", ""),
                            avatar_icon = user.get("avatar", dict()).get("avatar_origin", ""),
                            email = user.get("email", ""),
                            mobile = user.get("mobile", ""),
                            feishu_user_id = user.get("user_id", ""),
                            feishu_user_union_id = user.get("union_id", "")
                    )
            session.add_all([user_model])
            session.commit()
            session.close()

    print("flush feishu user done")

