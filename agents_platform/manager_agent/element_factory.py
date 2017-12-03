import math

import logger
from manager_agent.tags_reader import read_tags_str

TAG_OPEN = "@"
TAG_CLOSE = ":"


def generate_elements(agents, topics, elemental):
    board = elemental.get_board()
    elements = board.get_elements()
    # list all elements on board
    for element in elements:
        data = element.get_name()
        tag = ""
        try:
            # get tag of current element
            tag = data[data.index(TAG_OPEN):data.index(TAG_CLOSE)] + ": "
        except ValueError as ex:
            logger.exception('element_factory', 'topics exception')

        # if such tag is in our list
        if tag in agents:
            # remove it from our list
            agents.remove(tag)
            # this tag already have some topics
            existing_topics = read_tags_str(tag, element)
            # difference between ours
            diff = existing_topics - topics
            # union with ours
            union = existing_topics | topics
            # if there is difference
            if diff:
                # caption is our tag
                caption = tag
                # and all topics
                for i in union:
                    caption += i + ", "
                caption = caption[:len(caption) - 2]
                # update element on board
                board.update_element(element.get_posX(), element.get_posY(),
                                     element.get_id(), element.get_sizeX(),
                                     element.get_sizeY(), caption)
    # if some agents still not added
    if agents:
        for agent in agents:
            # get non empty and empty places
            element_matrix = board.get_elements_matrix()

            # find empty position
            pos_x = elemental.posX()
            pos_y = elemental.posY()
            size_x = 1
            size_y = 1

            k = 1
            should_go = True

            while should_go:
                for i in element_matrix:
                    for j in element_matrix[i]:
                        if math.fabs(i - pos_y) <= k and math.fabs(j - pos_x) <= k and element_matrix[i][j] == 0:
                            pos_y = i
                            pos_x = j
                            should_go = False
                k += 1
                if k > 100:
                    logger.error('element_factory', "no free space left")

            # caption is our tag
            caption = agent
            # and all topics
            for i in topics:
                caption += i + ", "
            caption = caption[:len(caption) - 2]

            # create element on board
            board.add_element(pos_x, pos_y, size_x, size_y, caption)
