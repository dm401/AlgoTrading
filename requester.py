import requests
from consts import IG_BASE_URL
import logging 

class IGSession:
    IG_BASE_URL = IG_BASE_URL
    base_headers = {
        "X-IG-API-KEY": "43b225011d6e7f5b301c4a0c7ad5cbd4a2a86dc9",
        "IG-ACCOUNT-ID": "Z27H4",
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json; charset=UTF-8",
        "VERSION": "3"
    }
    def __init__(self, creds):
        self.creds = creds
        self.req_session = requests.session()
        self.auth_headers = {}

    def get_initial_access_token(self):
        login_resp = self.req_session.post(
            url=IG_BASE_URL.format("session"), json=self.creds, headers=self.base_headers
        ).json()
        tokens = login_resp.get("oauthToken")
        self.tokens = tokens
        self.auth_headers = self.base_headers.update({
            "Authorization": "Bearer {}".format(self.tokens.get("access_token"))
        })


    def req(self, url, method, *args, n=0, **kwargs):
        resp=None
        try:
            resp = self.req_session.request(url=url, method=method, headers=self.auth_headers, *args, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as exc:
            if resp.status_code in [401] and "token-invalid" in resp.text:
                logging.info("invalid, refreshing")
                self.get_initial_access_token()
                if n < 3:
                    return self.req(url, method, *args, **kwargs)
                else:
                    logging.info("Exceeded max retries")
                    return None


