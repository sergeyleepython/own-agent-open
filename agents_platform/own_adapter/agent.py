import json
import urllib
from urllib import request

import logger
from own_adapter.board import Board


class Agent(object):
    def __init__(self, platform_access):
        self.__platform_access = platform_access

    def get_platform_access(self):
        return self.__platform_access;

    def get_boards(self):
        boards = []
        http_method = 'GET'
        detail = 'discoveryResponse'
        url = self.__platform_access.get_platform_url()
        values = {}
        try:
            headers = self.__platform_access.get_headers(http_method, url, values, detail)
            boards_request = urllib.request.Request(url, headers=headers)
            response = request.urlopen(boards_request)
            response_body = response.read().decode()
            response_dict = json.loads(response_body)
            boards = self.__create_boards(response_dict)
        except Exception as e:
            logger.exception('own_adapter', 'Could not get boards list. Exception message: {}'.format(str(e)))

        return boards

    def __create_boards(self, dictionary):
        boards = []
        for board in dictionary['boards']:
            name = board['rel']
            href = board['href']
            identifier = href.split('/')[-1]
            boards.append(Board(self.__platform_access, name, href, identifier))
        return boards
