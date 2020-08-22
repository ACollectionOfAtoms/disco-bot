import requests
import urllib

URBAN_DICTIONARY_URI = 'http://api.urbandictionary.com/v0/'

def get_first_ud_definition(search_term):
    uri_ready_search_term = urllib.parse.quote(search_term.strip(), safe='')
    uri = '{}define?term={}'.format(URBAN_DICTIONARY_URI, uri_ready_search_term)
    resp = requests.get(uri)
    json_resp = resp.json()
    definition_list = json_resp.get('list')
    no_list_returned = not definition_list
    list_is_empty = (type(definition_list) == list) and len(definition_list) < 1
    if no_list_returned or list_is_empty:
      return ''
    first_def_obj = definition_list[0]
    return first_def_obj.get('definition', '')
