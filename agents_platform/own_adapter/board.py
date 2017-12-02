import json
import re
import urllib
from urllib import request, error

import logger
from own_adapter.element import Element


class Board:
    def __init__(self, platform_access, name='', href='', identifier=''):
        self.__platform_access = platform_access
        self.__name = name
        self.__url = platform_access.get_platform_url() + href
        self.__id = identifier

    def get_name(self):
        return self.__name

    def get_url(self):
        return self.__url

    def get_id(self):
        return self.__id

    def get_elements(self, regexp=''):
        """Returns elements that belong to the board"""
        response_body = self.__elements_request()
        response_dict = json.loads(response_body)
        elements = self.__create_elements(response_dict, regexp)
        return elements

    @staticmethod
    def get_board_by_id(board_id, platform_access, need_name=True):
        """Gets an element by its id and returns it"""
        name = ''
        href = board_id
        if need_name:
            http_method = 'GET'
            detail = 'boards'
            url = '{}{}'.format(platform_access.get_platform_url(), board_id)
            values = {}
            headers = platform_access.get_headers(http_method, url, values, detail)
            board_request = request.Request(url, headers=headers)
            board_request.get_method = lambda: http_method
            response = request.urlopen(board_request).read().decode()
            name = json.loads(response)['board']['name']

        identifier = href.split('/')[-1]
        board = Board(platform_access, name, href, identifier)

        return board

    def __elements_request(self):
        """Requests elements from the backend"""
        http_method = 'GET'
        detail = 'elements'
        url = self.__url + '/elements'
        values = {}
        headers = self.__platform_access.get_headers(http_method, url, values, detail)
        elements_request = request.Request(url, headers=headers)
        elements_request.get_method = lambda: http_method
        response = request.urlopen(elements_request).read().decode()
        return response

    def __create_elements(self, dictionary, regexp):
        """Creates instances of Element from a dictionary"""
        elements = []
        for element in dictionary['elements']:
            href = element['_links'][0]['href']
            name = element['caption']
            if re.match(regexp, name):
                element = Element(self.__platform_access, name, href, self)
                elements.append(element)
        return elements

    def put_message(self, message):
        """Puts a message to the board chat"""
        http_method = 'POST'
        url = self.__url + '/posts'
        detail = 'post'

        payload = """
          {
            "post": {
              "message": \"""" + message + """\"
            }
          }
        """

        payload = json.dumps(json.loads(payload), separators=(',', ':'))
        values = {}
        headers = self.__platform_access.get_headers(http_method, url, values, detail, payload=payload)
        put_message_request = request.Request(url, headers=headers, data=payload.encode())
        put_message_request.get_method = lambda: http_method
        response = request.urlopen(put_message_request)
        response_status = response.getcode()

        return response_status

    def __get_board_size(self):
        """Returns board size"""
        http_method = 'GET'
        detail = 'board'
        url = self.__url
        values = {}

        headers = self.__platform_access.get_headers(http_method, url, values, detail)

        board_request = request.Request(url, headers=headers)
        board_request.get_method = lambda: http_method

        response = request.urlopen(board_request)
        response_body = response.read().decode()
        response_dict = json.loads(response_body)
        board_size = {'sizeX': response_dict['board']['sizeX'], 'sizeY': response_dict['board']['sizeY']}
        return board_size

    def get_elements_matrix(self):
        """Returns a matrix of board elements"""
        board_size = self.__get_board_size()
        response_body = self.__elements_request()
        response_dict = json.loads(response_body)
        elements_matrix = self.__create_elements_matrix(board_size, response_dict)
        return elements_matrix

    @staticmethod
    def __create_elements_matrix(board_size, response_dict):
        """Creates a matrix of board elements"""
        elements_matrix = [[0] * board_size['sizeX'] for i in range(board_size['sizeY'])]
        for element in response_dict['elements']:
            for i in range(1, element['sizeY'] + 1):
                for j in range(1, element['sizeX'] + 1):
                    try:
                        elements_matrix[element['posY'] + i - 2][element['posX'] + j - 2] = 1
                    except IndexError as e:
                        logger.exception('own_adapter',
                                         'Failed to create elements matrix. Error message: {}'.format(str(e)))
                        elements_matrix = [[1] * board_size['sizeX'] for i in range(board_size['sizeY'])]
                        return elements_matrix
        return elements_matrix

    def add_element(self, pos_x, pos_y, size_x=1, size_y=1, caption=''):
        """ Puts a new element on the board.
            Two steps:
            1. Add an element with empty name (no message on the board chat);
            2. Add a caption to new element (message on the board chat)"""
        new_element_link = ''
        try:
            http_method = 'POST'
            detail = 'activities'
            url = self.__url + '/elements'

            payload = """
                {
                  "element": {
                    "posX": \"""" + str(pos_x) + """\",
                    "posY": \"""" + str(pos_y) + """\",
                    "sizeX": \"""" + str(size_x) + """\",
                    "sizeY": \"""" + str(size_y) + """\",
                    "type": "MultiInput",
                    "caption": ""
                  }
                }
              """

            payload = json.dumps(json.loads(payload), separators=(',', ':'))
            values = {}
            headers = self.__platform_access.get_headers(http_method, url, values, detail, payload=payload)
            add_element_request = request.Request(url, headers=headers, data=payload.encode())
            add_element_request.get_method = lambda: http_method
            response = request.urlopen(add_element_request)
            response_dict = json.loads((response.read().decode()))
            new_element_link = response_dict["element"]["_links"][0]["href"]

        except urllib.error.HTTPError as e:
            logger.exception('own_adapter',
                             'Error: add element to {} failed. Error type: {}'.format(self.get_name(), str(e)))
            return e.code
        # add element name (creation of the message on the board chat)
        try:
            http_method = 'PUT'
            detail = 'element'
            url = self.__platform_access.get_platform_url() + new_element_link

            payload = """
                        {
                          "element": {
                            "posX": \"""" + str(pos_x) + """\",
                            "posY": \"""" + str(pos_y) + """\",
                            "sizeX": \"""" + str(size_x) + """\",
                            "sizeY": \"""" + str(size_y) + """\",
                            "type": "MultiInput",
                            "caption": \"""" + caption + """\"
                          }
                        }
                      """

            payload = json.dumps(json.loads(payload), separators=(',', ':'))
            values = {}
            headers = self.__platform_access.get_headers(http_method, url, values, detail, payload=payload)
            add_name_request = request.Request(url, headers=headers, data=payload.encode())
            add_name_request.get_method = lambda: http_method
            response = request.urlopen(add_name_request)
            response_status = response.getcode()
            return response_status
        except urllib.error.HTTPError as e:
            logger.exception('own_adapter',
                             'Error: add element name {} to {} failed. Error type: {}'.format(caption, self.get_name(),
                                                                                              str(e)))
            return e.code

    def remove_element(self, element_url):
        """Removes an element from the board"""
        try:
            http_method = 'DELETE'
            detail = 'element'
            url = element_url
            values = {}
            headers = self.__platform_access.get_headers(http_method, url, values, detail)
            elements_request = request.Request(url, headers=headers)
            elements_request.get_method = lambda: http_method
            response = request.urlopen(elements_request)
            return response.getcode()
        except urllib.error.HTTPError as e:
            logger.exception('own_adapter',
                             'Error: remove element {} from {} failed. Error type: {}'.format(element_url,
                                                                                              self.get_name(), str(e)))
            return e.code
