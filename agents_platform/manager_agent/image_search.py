import requests
import json

startIndex = '1'
key = 'AIzaSyDG-gNt2kp_MQeaQIqOO97h5g_HjPljs0g'
cx = '007202563605979946646:h4yc2e0zpbi'

def get_image_links(searchTerm):
    searchUrl = "https://www.googleapis.com/customsearch/v1?q=" + \
                searchTerm + "&start=" + startIndex + "&key=" + key + "&cx=" + cx + "&searchType=image"
    r = requests.get(searchUrl)
    response = r.content.decode('utf-8')
    result = json.loads(response)
    links = [item['link'] for item in result['items']]
    return links

if __name__ == '__main__':
    links = get_image_links('apple')
    print(links)