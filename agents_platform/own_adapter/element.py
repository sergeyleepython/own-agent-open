import json
import urllib
from datetime import datetime
from urllib import request, error

import requests

import logger
from own_adapter.file import File


class Element:
    __name = ''
    __url = ''
    __posX = 0
    __posY = 0
    __sizeX = 0
    __sizeY = 0
    __board = None
    __last_processing_time = None
    __id = ''

    def __init__(self, platform_access, name='', identifier='', board=None, sizeX=2, sizeY=2, posX=1, posY=1, link='',
                 last_processing_time=datetime.strptime('2000.01.01 00:00:00', '%Y.%m.%d %H:%M:%S')):
        self.__platform_access = platform_access
        self.__name = name
        self.__url = platform_access.get_platform_url() + identifier
        self.__id = identifier
        self.__board = board
        self.__last_processing_time = last_processing_time
        self.__sizeX = sizeX
        self.__sizeY = sizeY
        self.__posX = posX
        self.__posY = posY

    def get_url(self):
        return self.__url

    def get_posX(self):
        return self.__posX

    def get_posY(self):
        return self.__posY

    def get_sizeX(self):
        return self.__sizeX

    def get_sizeY(self):
        return self.__sizeY

    def get_name(self):
        return self.__name

    def get_id(self):
        return self.__id

    def get_board(self):
        return self.__board

    def get_last_processing_time(self):
        return self.__last_processing_time

    def set_last_processing_time(self, last_processing_time):
        assert (isinstance(last_processing_time, datetime))
        self.__last_processing_time = last_processing_time

    def to_dictionary(self):
        """Returns the element serialized to a dictionary"""
        element_dict = dict()
        element_dict['name'] = self.__name
        element_dict['id'] = self.__id

        if self.__last_processing_time is not None:
            element_dict['last_processing_time'] = self.__last_processing_time.strftime('%Y.%m.%d %H:%M:%S')
        else:
            element_dict['last_processing_time'] = ''

        return element_dict

    @staticmethod
    def from_dictionary(platform_access, element_dict):
        """Deserializes the given dict and returns a new element"""
        name = element_dict['name']
        id = element_dict['id']

        str_last_processing_time = element_dict.get('last_processing_time', '')
        if str_last_processing_time == '':
            last_processing_time = datetime.strptime('2000.01.01 00:00:00', '%Y.%m.%d %H:%M:%S')
        else:
            last_processing_time = datetime.strptime(str_last_processing_time, '%Y.%m.%d %H:%M:%S')
        element = Element(platform_access, name, id, last_processing_time=last_processing_time)

        return element

    def get_files(self):
        """Returns a collection of File instances of the element files"""
        http_method = 'GET'
        detail = 'board'
        url = self.__url + '/files'
        values = {}
        headers = self.__platform_access.get_headers(http_method, url, values, detail)

        files_request = request.Request(url, headers=headers)

        response = request.urlopen(files_request)
        response_body = response.read().decode()
        response_dict = json.loads(response_body)

        files = self.__create_files(response_dict)
        return files

    def __create_files(self, dictionary):
        """Creates files from a dictionary"""
        files = []
        for element in dictionary['files']:
            href = element['_links'][0]['href']
            name = element['name']
            file_type = element['fileType']
            files.append(File(self.__platform_access, name, href, file_type))
        return files

    def put_link(self, link, default_image_url='https://www.own.space/images/other/htmlrefdefault.png'):
        """Puts a link to the element"""
        try:
            http_method = 'POST'
            detail = "htmlReference"
            url = self.__url + "/files"

            additional_headers = {'Content-Type': 'application/json; charset=UTF-8'}

            payload = """
              {{
                "htmlReference": {{
                  "url": "{0}",
                  "defaultImageUrl": "{1}"
                }}
              }}
            """.format(link, default_image_url)

            payload = ''.join(payload.split())

            values = {}

            headers = self.__platform_access.get_headers(http_method, url, values, detail, payload=payload,
                                                         additional_headers=additional_headers)

            link_request = request.Request(url, headers=headers, data=payload.encode())

            response = request.urlopen(link_request)
            response_status = response.getcode()

            return response_status
        except urllib.error.HTTPError as e:
            logger.exception('own_adapter',
                             'Error: put link {} to {} failed. Error type: {}'.format(link, self.get_name(), str(e)))
            return e.code
        except Exception as e:
            logger.exception('own_adapter',
                             'Error: put link {} to {} failed. Error type: {}'.format(link, self.get_name(), str(e)))
            return 0

    def put_file(self, file_name, file_bytes):
        """Puts an arbitrary file to the element"""
        # use this for multipart/form-data
        # https://stackoverflow.com/questions/6260457/using-headers-with-the-python-requests-librarys-get-method
        # additional reference
        # https://stackoverflow.com/questions/4007969/application-x-www-form-urlencoded-or-multipart-form-data
        # to dump raw requests/responses you can use http://toolbelt.readthedocs.io/en/latest/dumputils.html
        try:
            http_method = 'POST'
            detail = 'fileCreationResponse'
            url = self.__url + '/files'
            additional_headers = {}
            payload = ''
            values = {}

            headers = self.__platform_access.get_headers(http_method, url, values, detail, payload=payload,
                                                         additional_headers=additional_headers)

            response = requests.post(url, headers=headers, files={file_name: file_bytes})
            response_status = response.status_code

            return response_status
        except urllib.error.HTTPError as e:
            logger.exception('own_adapter',
                             'Error: put file {} to {} failed. Error type: {}'.format(file_name, self.get_name(),
                                                                                      str(e)))
            return e.code
        except Exception as e:
            logger.exception('own_adapter',
                             'Error: put file {} to {} failed. Error type: {}'.format(file_name, self.get_name(),
                                                                                      str(e)))
            return 0

    def remove_file(self, file_link):
        """Removes a file from the element"""
        try:
            http_method = 'DELETE'
            detail = 'board'
            url = file_link
            values = {}

            headers = self.__platform_access.get_headers(http_method, url, values, detail)

            remove_request = request.Request(url, headers=headers)
            remove_request.get_method = lambda: 'DELETE'

            response = request.urlopen(remove_request)
            response_status = response.getcode()

            logger.debug('own_adapter', response_status)

            return response_status
        except urllib.error.HTTPError as e:
            logger.exception('own_adapter',
                             'Error: remove file {} from {} failed. Error type: {}'.format(file_link, self.get_name(),
                                                                                           str(e)))
            return e.code

    @staticmethod
    def get_element_by_id(element_id, platform_access, board):
        """Gets an element by its id and returns it"""
        http_method = 'GET'
        detail = 'elements'
        url = '{}{}'.format(platform_access.get_platform_url(), element_id)
        values = {}
        headers = platform_access.get_headers(http_method, url, values, detail)
        elements_request = request.Request(url, headers=headers)
        elements_request.get_method = lambda: http_method
        response = request.urlopen(elements_request).read().decode()
        element_dict = json.loads(response)

        href = element_dict['element']['_links'][0]['href']
        name = element_dict['element']['caption']
        element = Element(platform_access, name, href, board)

        return element
