import os
import requests

class UnknownSectionError(Exception):
  pass

NYT_KEY = os.environ['NYT_KEY']
NYT_URL = 'https://api.nytimes.com/svc/topstories/v2'

VALID_SECTIONS = ['arts', 'automobiles', 'books', 'business', 'fashion', 'food', 'health', 'home', 'insider', 'magazine', 'movies', 'nyregion', 'obituaries', 'opinion', 'politics', 'realestate', 'science', 'sports', 'sundayreview', 'technology', 'theater', 't-magazine', 'travel', 'upshot', 'us', 'world.']

def get_headlines_response(section):
  if section not in VALID_SECTIONS:
    raise UnknownSectionError()
  uri = '{}/{}.json?api-key={}'.format(NYT_URL, section, NYT_KEY)
  resp = requests.get(uri)
  if resp['status'] != 'OK':
    raise Exception('Could not fetch data: {}'.format(resp))
  return resp.json()

def parse_first_three_titles(nyt_resp):
  results = nyt_resp['results']
  first_three = results[:3]
  titles = [a['title'] for a in first_three]
  return titles

"""
Returns a list of headlines.
"""
def get_headlines(section):
  headlines = get_headlines_response(section)
  titles = parse_first_three_titles(headlines)
  return titles
