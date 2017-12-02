import base64
import datetime
import json
import sys
import urllib
from urllib import request

import logger

OWN_PLATFORM_ADDRESS = 'http://188.130.155.101:9000'


class PlatformAccess:
    __platform_url = ''
    __access_token = ''
    __secret_token = ''
    __login = ''
    __password = ''

    def __init__(self, login, password):
        self.__login = login
        self.__password = password
        self.__access_token_request()

    def get_access_token(self):
        return self.__access_token

    def get_platform_url(self):
        return self.__platform_url

    def get_headers(self, method, url, values, detail, environment='production', payload='', additional_headers=None):
        return self.__generate_headers(method, url, datetime.datetime.utcnow(), values, detail, environment,
                                       payload, additional_headers)

    def __access_token_request(self):
        address = OWN_PLATFORM_ADDRESS

        values = """
              {
                "accessTokenRequest": {
                  "clientId": "we2$%6etetertef",
                  "grantType": "password"
                }
              }
            """.encode()

        auth = base64.b64encode(('%s:%s' % (self.__login, self.__password)).encode())
        detail = 'accessTokenRequest'
        url = '/accesstokens'

        headers = {
            'Accept': 'application/vnd.uberblik.' + detail + '+json',
            'Authorization': 'Basic ' + auth.decode()
        }

        token_request = urllib.request.Request(address + url, data=values, headers=headers)

        try:
            response_body = request.urlopen(token_request).read().decode()
        except Exception as e:
            logger.exception('own_adapter', 'Authorization failed.\nurl = {}\nheaders = {}\nException message: {}'.format(address + url, headers, str(e)))
            sys.exit(1)
        else:
            dictionary = json.loads(response_body)

            self.__platform_url = address
            self.__access_token = dictionary['accessToken']['token']
            self.__secret_token = dictionary['accessToken']['secret']

    def __generate_headers(self, method, url, now, values, detail, environment, payload='', additional_headers=None):
        if additional_headers is None:
            additional_headers = dict()
        timestamp = now.isoformat()[:-3] + "Z"  # ISO8601 formatted timestamp

        headers = {
            'Accept': 'application/vnd.uberblik.{}+json'.format(detail),
            'access-token': self.__access_token,
            'x-uberblik-timestamp': timestamp
        }

        headers.update(additional_headers)

        return headers
