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
        agent = ""
        try:
            # get tag of current element
            agent = data[data.index(TAG_OPEN):data.index(TAG_CLOSE)] + ": "
        except ValueError as ex:
            logger.exception('element_factory', 'topics exception')

        # if such tag is in our list
        if agent in agents:
            # remove it from our list
            agents.remove(agent)
            # this tag already have some topics
            existing_topics = read_tags_str(agent, element)
            # difference between ours
            diff = set(topics).difference(existing_topics)
            # union with ours
            union = set(existing_topics).union(topics)
            # if there is difference
            if diff:
                # caption is our tag
                caption = agent
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
        used = []
        for agent in agents:
            # get non empty and empty places
            element_matrix = board.get_elements_matrix()

            # find empty position
            pos_x = elemental.get_posX()
            pos_y = elemental.get_posY()
            size_x = 1
            size_y = 1

            k = 1
            should_go = True

            while should_go:
                for j, sublist in enumerate(element_matrix):
                    for i, element in enumerate(sublist):
                        if math.fabs(j - pos_y) <= k and math.fabs(i - pos_x) <= k and element == 0 \
                                and not (i, j) in used:
                            pos_y = j
                            pos_x = i
                            used.append((pos_x, pos_y))
                            should_go = False
                            break
                    if not should_go:
                        break
                k += 1
                if k > 10:
                    logger.error('element_factory', "no free space left")

            # caption is our tag
            caption = agent
            # and all topics
            topics = ', '.join(topics)
            caption = caption + topics

            # create element on board
            board.add_element(pos_x, pos_y, size_x, size_y, caption)
