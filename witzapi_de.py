#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Witzapi_de module for InkyCal Project
Special thanks to Erik Fredericks (@efredericks) for the template!
I've slightly adjusted this module for use with witzapi.de:
https://github.com/aceisace/Inkycal/blob/main/inkycal/modules/inkycal_jokes.py
"""
from inkycal.modules.template import inkycal_module
from inkycal.custom import *

import requests
# Show less logging for request module
logging.getLogger("urllib3").setLevel(logging.WARNING)

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)

class Witzapi_de(inkycal_module):
  """Witzapi_de class
  gets a joke from witzapi.de
  """

  name = "witzapi.de API - grab a random joke from witzapi.de api"

  categories_list = ['all']
  categories_json = requests.get('https://witzapi.de/api/category',timeout=10).json()
  for category in categories_json:
    categories_list.append(category['name'])

  requires = {
    'category': {
                  "label": "Choose your category",
                  "options": [ categories_list ],
                }
  }

  def __init__(self, config):
    """Initialize inkycal_feeds module"""

    super().__init__(config)

    config = config['config']

    self.category = config['category']

    # give an OK message
    print(f'{filename} loaded')

  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding
    im_width = int(self.width - (2 * self.padding_left))
    im_height = int(self.height - (2 * self.padding_top))
    im_size = im_width, im_height
    logger.info(f'image size: {im_width} x {im_height} px')

    # Create an image for black pixels and one for coloured pixels
    im_black = Image.new('RGB', size = im_size, color = 'white')
    im_colour = Image.new('RGB', size = im_size, color = 'white')

    # Check if internet is available
    if internet_available() == True:
      logger.info('Connection test passed')
    else:
      raise Exception('Network could not be reached :/')

    # Set some parameters for formatting feeds
    line_spacing = 1
    line_height = self.font.getsize('hg')[1] + line_spacing
    line_width = im_width
    max_lines = (im_height // (self.font.getsize('hg')[1] + line_spacing))

    logger.debug(f"max_lines: {max_lines}")

    # Calculate padding from top so the lines look centralised
    spacing_top = int( im_height % line_height / 2 )

    # Calculate line_positions
    line_positions = [
      (0, spacing_top + _ * line_height ) for _ in range(max_lines)]

    logger.debug(f'line positions: {line_positions}')

    if self.category == 'all':
      category_param = ''
    else:
      category_param = '?category=' + self.category

    # Get the actual joke
    url    = 'https://witzapi.de/api/joke' + category_param
    header = {'accept': 'application/json'}
    response = requests.get(url, headers=header)
    response.encoding = 'utf-8' # Change encoding to UTF-8
    joke = response.json()[0]['text'].rstrip() # use to remove newlines
    logger.debug(f"joke: {joke}")

    # wrap text in case joke is too large
    wrapped = text_wrap(joke, font = self.font, max_width = line_width)
    logger.debug(f"wrapped: {wrapped}")

    # Check if joke can actually fit on the provided space
    if len(wrapped) > max_lines:
      logger.error("Ohoh, Joke is too large for given space, please consider "
            "increasing the size for this module")

    # Write the joke on the image
    for _ in range(len(wrapped)):
      if _+1 > max_lines:
        logger.error('Ran out of lines for this joke :/')
        break
      write(im_black, line_positions[_], (line_width, line_height),
            wrapped[_], font = self.font, alignment= 'left')

    # Return images for black and colour channels
    return im_black, im_colour


if __name__ == '__main__':
  print(f'running {filename} in standalone/debug mode')
