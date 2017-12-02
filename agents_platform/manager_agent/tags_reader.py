import logger

TAG_OPEN = "@"
TAG_TOPICS = "@topics:"
TAG_VOICE = "@voice:"
VOICE_ON = "on"


def read_tags_str(tag, element):
    data = element.get_name()
    s = 0
    e = 1000
    try:
        s = data.index(tag) + len(tag)
        e = data.index(TAG_OPEN, data.index(tag) + len(tag))
    except ValueError as ex:
        logger.exception('tags_reader', 'topics exception')

    topics = data[s:e]
    topics_list = map(str.strip, topics.split(","))

    return topics_list


def read_tags_bool(tag, element):
    if VOICE_ON in read_tags_str(tag, element):
        return True
    return False


def read_tags(element):
    topics_list = read_tags_str(TAG_TOPICS, element)
    is_voice = read_tags_bool(TAG_VOICE, element)

    return topics_list, is_voice
