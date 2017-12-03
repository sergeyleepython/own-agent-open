# TODO mock-up file
# need base of all agents with description to deduce
# what agent we should peak depending on topic

PROGRAMMING_TAG = "programming"
HOTEL_TAG = "hotel"


def get_agents(topics, tags):
    result = ["@news: "]
    agents = ["@news: ", "@github: ", "@pics: "]
    programming_agents = ["@github: "]
    hotel_agents = ["@pics: "]

    # TODO some interaction with agents base here

    if PROGRAMMING_TAG in tags:
        result = result.extend(programming_agents)
    if HOTEL_TAG in tags:
        result = result.extend(hotel_agents)
    return list(set(result))
