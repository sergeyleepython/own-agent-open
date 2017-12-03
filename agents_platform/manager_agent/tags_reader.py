import logger

TAG_OPEN = "@"
TAG_TOPICS = "@topics:"
TAG_VOICE = "@voice:"
VOICE_ON = "on"


def read_tags_str(topics_tag, element):
    data = element.get_name()
    if topics_tag in data:
        topics = data.split(topics_tag)[-1]
        topics = topics.split('@')[0]
        topics_list = [topic.strip() for topic in topics.split(',') if topic.strip()]
    else:
        topics_list = []
    return topics_list


def read_tags_bool(tag, element):
    if VOICE_ON in read_tags_str(tag, element):
        return True
    return False


def read_tags(element):
    topics_list = read_tags_str(TAG_TOPICS, element)
    is_voice = read_tags_bool(TAG_VOICE, element)

    return topics_list, is_voice
