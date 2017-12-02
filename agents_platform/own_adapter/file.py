import json
from urllib import request

import logger


class File:
    __name = ""
    __url = ""
    __type = ""

    def __init__(self, platform_access, name, identifier, file_type):
        self.__platform_access = platform_access
        self.__name = name
        self.__url = platform_access.get_platform_url() + identifier
        self.__type = file_type

    def get_name(self):
        return self.__name

    def get_type(self):
        return self.__type

    def get_url(self):
        return self.__url

    def get_download_link(self):
        # there is no download link to files with type "htmlReference"
        if self.__type == "application/vnd.uberblik.htmlReference":
            return None
        http_method = 'POST'
        detail = "downloadLink"
        url = self.__url + "/downloadLink"
        values = {}

        headers = self.__platform_access.get_headers(http_method, url, values, detail)

        link_request = request.Request(url, headers=headers)
        link_request.get_method = lambda: http_method
        response = request.urlopen(link_request)
        response_body = response.read().decode()

        response_dict = json.loads(response_body)
        download_link = response_dict["downloadLink"]["url"]

        return download_link

    def remove(self):
        """Removes itself from an element"""
        http_method = 'DELETE'
        detail = "board"
        url = self.__url
        values = {}

        headers = self.__platform_access.get_headers(http_method, url, values, detail)

        remove_request = request.Request(url, headers=headers)
        remove_request.get_method = lambda: 'DELETE'

        response = request.urlopen(remove_request)
        response_status = response.getcode()

        logger.debug('own_adapter', response_status)

        return response_status
