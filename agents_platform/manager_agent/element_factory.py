import logger
from manager_agent.tags_reader import read_tags_str

TAG_OPEN = "@"
TAG_CLOSE = ":"


def generate_elements(agents, topics, board):
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
            # TODO find empty spaces !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            # find empty position
            pos_x = 1
            pos_y = 1
            size_x = 2
            size_y = 2

            # caption is our tag
            caption = agent
            # and all topics
            for i in topics:
                caption += i + ", "
            caption = caption[:len(caption) - 2]

            # create element on board
            board.add_element(pos_x, pos_y, size_x, size_y, caption)