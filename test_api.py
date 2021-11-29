import requests
from requests.api import head
import json
from consts import IG_BASE_URL
from passwordstuff import base_headers, creds


s = requests.session()

# Initial login req
print(IG_BASE_URL.format("session"))
login_resp = s.post(url=IG_BASE_URL.format("session"), json=creds, headers=base_headers).json()

print("Got login details!", json.dumps(login_resp, indent=2))

tokens = login_resp.get("oauthToken")


authed_headers = {
    "Authorization": "Bearer {}".format(tokens.get("access_token"))
}
base_headers.update(authed_headers)
base_headers["VERSION"] = ""
resp = requests.get(
    url=IG_BASE_URL.format("/watchlists"),
    headers=base_headers
)


print(resp, json.dumps(resp.json(), indent=2))
