# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import requests

ENV = "dev"
URL = "http://configserver-{env}.chj.cloud/configs/{appName}/default/application"
#URL = "http://127.0.0.1:8080/configs/{app_name}/default/application"

env = os.getenv("RUNTIME_ENV") or ENV

def get_apollo_config(k, app_name):
    data = requests.get(URL.format(app_name=app_name))

    if data.status_code == 200:
        return data.json()["configurations"][k]
    else:
        return ""
