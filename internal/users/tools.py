
#获取飞书 access_token
def get_tenant_access_token(app_id="", app_secret=""):
    import json
    import requests

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": app_id, "app_secret": app_secret}

    return requests.post(url, headers=headers, data=json.dumps(data)).json()

#封装飞书所有接口请求, 在header中增加authorization控制
def feishu_requests_main(method, url, data=dict(), app_id="", app_secret=""):
    import json
    import requests

    token_data = get_tenant_access_token(app_id, app_secret)
    if token_data.get("code", "") == 0:
        headers = {"Content-Type": "application/json", "Authorization": "Bearer "+token_data.get("tenant_access_token")}
    else:
        return {"code": 403, "msg": "获取token失败"}

    if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
        if isinstance(data, dict) or isinstance(data, str):
            if method.upper() == "GET":
                response_data = requests.get(url, headers=headers).json()
            elif method.upper() == "POST":
                response_data = requests.post(url, headers=headers, data=json.dumps(data)).json()
            elif method.upper() == "PUT":
                response_data = requests.put(url, headers=headers, data=json.dumps(data)).json()
            elif method.upper() == "POST":
                response_data = requests.delete(url, headers=headers, data=json.dumps(data)).json()
            elif method.upper() == "PATCH":
                response_data = requests.patch(url, headers=headers, data=json.dumps(data)).json()
            return response_data
        else:
            return {"code": 400, "msg": "data error"}
    else:
        return {"code": 400, "msg": "method %s not allow"%method}


class RedisManage(object):
    
    def __init__(self, host=None, port=6379, db=0, sentinels=list(), clusterName=None, passwd=None, connect_type="direct", S="redisManage"):
        '''
            connect_type: None(直接连接) spool(连接池) sentinel(哨兵模式)  暂时不支持cluster模式
        '''
        import redis
        from redis.sentinel import Sentinel

        self.host = host
        self.port = port
        self.db = db
        self.sentinels = sentinels
        self.clusterName = clusterName
        self.passwd = passwd
        self.connect_type = connect_type
        self.s = S 

        if not self.host and not self.sentinels and not self.clusterName and not self.passwd:
            raise "connection params error"
        else:
            if self.connect_type == "direct": #直接连接
                self.server = redis.Redis(host=self.host, port=self.port, db=self.db)

            elif self.connect_type == "spool": #连接池
                pool = redis.ConnectionPool(host=host, port=port)
                self.server = redis.Redis(connection_pool=pool, db=self.db)

            elif self.connect_type == "sentinel": #哨兵模式
                self.sentinel = Sentinel(self.sentinels, socket_timeout=1)
                self.master = self.sentinel.master_for(self.clusterName, password=self.passwd)
                self.slave = self.sentinel.slave_for(self.clusterName, password=self.passwd)

            else:
                raise "connect type error [spool|sentinel]"

    def get(self, key):
        import json

        key = "{s}-{key}".format(s=self.s, key=key)

        if self.connect_type == "sentinel":
            return json.loads(self.slave.get(key))
        elif self.connect_type in ["direct", "spool"]:
            return json.loads(self.server.get(key))
        else:
            return "connect type error [spool|sentinel]"            

    def set(self, key, value):
        import json

        key = "{s}-{key}".format(s=self.s, key=key)        

        if self.connect_type == "sentinel":
            self.master.set(key, json.dumps(value))
            self.master.expire(key, 43200)
        elif self.connect_type in ["direct", "spool"]:
            self.server.set(key, json.dumps(value))
            self.server.expire(key, 43200)
        else:
            return "connect type error [spool|sentinel]"


