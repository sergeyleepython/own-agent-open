import json
import re
import threading
import time
import traceback

import speech_recognition as sr
import websocket

import logger
from manager_agent.agent_deduct import get_agents
from manager_agent.element_factory import generate_elements
from manager_agent.nlp import TopicsGenerator
from manager_agent.tags_reader import read_tags
from own_adapter.agent import Agent
from own_adapter.board import Board
from own_adapter.element import Element
from own_adapter.platform_access import PlatformAccess

AGENT_LOGIN = 'daulettbot@gmail.com'
AGENT_PASSWORD = 'G@h0km_K.cz'

TOPIC_GENS = {}


def __do_something(element):
    """Write your code here"""

    # get tags and voice option
    domain_tags, is_voice = read_tags(element)
    recognized_message = ""
    # should agent work with voice?
    if domain_tags:
        for domain_tag in domain_tags:
            topics = domain_tags
            if is_voice:
                try:
                    # switch recognizer on
                    r = sr.Recognizer()
                    with sr.Microphone() as source:
                        logger.info('helloworld', 'ready to listen')
                        # listen till stop
                        audio = r.listen(source, phrase_time_limit=10, timeout=2)
                        # write message
                        recognized_message = r.recognize_google(audio)
                        # nlp
                        topic_gen = TOPIC_GENS.get(domain_tag)
                        if topic_gen is None:
                            topic_gen = TopicsGenerator(domain_tag=domain_tag)
                            TOPIC_GENS[domain_tag] = topic_gen
                        topics = topic_gen.candidates_wiki_tag_disambiguation(recognized_message)
                        logger.info('helloworld', "TEXT:" + recognized_message)
                except sr.UnknownValueError:
                    logger.error('helloworld', "Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    logger.error('helloworld',
                                 "Could not request results from Google Speech Recognition service; {0}".format(e))
            # get corresponding agents to this topics and tags
            agents = get_agents(domain_tag)
            # set them to work or update their tags
            generate_elements(agents, topics, element)


def __run_on_element(element):
    """Running on a target element"""
    try:
        __do_something(element)
    except Exception as ex:
        logger.exception('helloworld', 'Error: could not process an element. Element id: {}. Exception message: {}.\n'
                                       '{}'.format(element.get_id(), str(ex), traceback.format_exc()))


def __run_on_board(board):
    """Runs the agent on elements of a board"""
    elements = board.get_elements()
    for element in elements:
        __run_on_element(element)


def periodical_update():
    """Does periodical work with a predefined time interval"""
    time_interval = 5

    while True:
        time.sleep(time_interval)

        agent = get_agent()
        boards = agent.get_boards()
        for board in boards:
            __run_on_board(board)
        logger.info('helloworld', 'Daily news update is done.')


def get_agent():
    """Returns the current agent"""
    login = AGENT_LOGIN
    password = AGENT_PASSWORD

    platform_access = PlatformAccess(login, password)
    helloworld_agent = Agent(platform_access)

    return helloworld_agent


def on_websocket_message(ws, message):
    """Processes websocket messages"""
    message_dict = json.loads(message)
    content_type = message_dict['contentType']
    message_type = content_type.replace('application/vnd.uberblik.', '')

    logger.debug('helloworld', message)

    if message_type == 'liveUpdateElementCaptionEdited+json':
        element_caption = message_dict['newCaption']
        # looking for elements that target our agent
        if re.match(pattern='@helloworld:.+', string=element_caption):
            # create instances of Board and Element to work with them
            element_id = message_dict['path']
            news_agent = get_agent()
            board_id = '/'.join(element_id.split('/')[:-2])
            board = Board.get_board_by_id(board_id, news_agent.get_platform_access(), need_name=False)
            element = Element.get_element_by_id(element_id, news_agent.get_platform_access(), board)
            if element is not None:
                __run_on_element(element)


def on_websocket_error(ws, error):
    """Logs websocket errors"""
    logger.error('helloworld', error)


def on_websocket_open(ws):
    """Logs websocket openings"""
    logger.info('helloworld', 'Websocket is open')


def on_websocket_close(ws):
    """Logs websocket closings"""
    logger.info('helloworld', 'Websocket is closed')


def open_websocket():
    """Opens a websocket to receive messages from the boards about events"""
    agent = get_agent()
    # getting the service url without protocol name
    platform_url_no_protocol = agent.get_platform_access().get_platform_url().split('://')[1]
    access_token = agent.get_platform_access().get_access_token()
    url = 'ws://{}/opensocket?token={}'.format(platform_url_no_protocol, access_token)

    ws = websocket.WebSocketApp(url,
                                on_message=on_websocket_message,
                                on_error=on_websocket_error,
                                on_open=on_websocket_open,
                                on_close=on_websocket_close)
    ws.run_forever()


def run():
    websocket_thread = None
    updater_thread = None

    while True:
        # opening a websocket for catching server messages
        if websocket_thread is None or not websocket_thread.is_alive():
            try:
                websocket_thread = threading.Thread(target=open_websocket)
                websocket_thread.start()
            except Exception as e:
                logger.exception('helloworld', 'Could not open a websocket. Exception message: {}'.format(str(e)))

        # periodical updates
        if updater_thread is None or not updater_thread.is_alive():
            try:
                updater_thread = threading.Thread(target=periodical_update)
                updater_thread.start()
            except Exception as e:
                logger.exception('helloworld', 'Could not start updater. Exception message: {}'.format(str(e)))

        # wait until next check
        time.sleep(10)


if __name__ == '__main__':
    run()
