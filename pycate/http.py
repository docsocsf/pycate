import requests

from pycate.exceptions import ClientException


class Http(object):
    def __init__(self, user_agent):
        if not user_agent:
            raise ClientException("User agent error")
        self.user_agent = user_agent

    def get(self, url, username, password):
        if username is None or password is None:
            raise ClientException("Username or password is None")

        return requests.get(url, headers={
            'User-Agent': self.user_agent
        }, auth=(username, password))
