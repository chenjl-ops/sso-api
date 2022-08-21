import os
import sys

HERE = os.path.abspath(__file__)
HOME_DIR = os.path.split(os.path.split(HERE)[0])[0]
os.sys.path.append(HOME_DIR)

from apollo import apollo_manage

app_name = "sso-api"

mysql_db_name = apollo_manage.get_apollo_config("mysql_db_name", app_name)
mysql_db_user = apollo_manage.get_apollo_config("mysql_db_user", app_name)
mysql_db_host = apollo_manage.get_apollo_config("mysql_db_host", app_name)
mysql_db_port = apollo_manage.get_apollo_config("mysql_db_port", app_name)
mysql_db_passwd = apollo_manage.get_apollo_config("mysql_db_passwd", app_name)

redis_host = apollo_manage.get_apollo_config("redis_host", app_name)
redis_port = apollo_manage.get_apollo_config("redis_port", app_name)
feishu_api_url = apollo_manage.get_apollo_config("feishu_api_url", app_name)

base_redirect_url = apollo_manage.get_apollo_config("base_redirect_url", app_name)
feishu_app_id = apollo_manage.get_apollo_config("feishu_app_id", app_name)
feishu_app_secret = apollo_manage.get_apollo_config("feishu_app_secret", app_name)

if __name__ == "__main__":
    print("SSO-Api apolloConfig")
