import json
import requests
from base import URL_HTTP


def auth_broker(identifier, password):
    data = {
        "identifier": identifier,
        "password": password
    }
    auth = json.loads(requests.post(url=URL_HTTP, data=data).content)
    if auth["code"] == "success":
        return auth["ssid"]
    else:
        return None