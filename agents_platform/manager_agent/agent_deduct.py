# TODO mock-up file
# need base of all agents with description to deduce
# what agent we should peak depending on topic

mapping = {"programming": ["@github: "],
           "hotel": ["@pics: "]}

def get_agents(domain_tag):
    result = ["@news: "]

    # TODO some interaction with agents base here
    agents = mapping[domain_tag]
    result.extend(agents)
    return list(set(result))
