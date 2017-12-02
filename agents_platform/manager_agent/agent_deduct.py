# TODO mock-up file
# need base of all agents with description to deduce
# what agent we should peak depending on topic

PROGRAMMING_TAG = "programming"
HOTEL_TAG = "hotel"


def get_agents(topics, tags):
    agents = ["@news: ", "@github: ", "@pics: "]
    programming_agents = ["@news: ", "@github: "]
    hotel_agents = ["@news: ", "@pics: "]

    # TODO some interaction with agents base here

    if tags == PROGRAMMING_TAG:
        return programming_agents
    elif tags == HOTEL_TAG:
        return hotel_agents
    return agents
