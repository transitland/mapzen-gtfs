from setuptools import setup

import mzgtfs

setup(
  name='mzgtfs',
  version=mzgtfs.__version__,
  description='Mapzen GTFS',
  author='Ian Rees',
  author_email='ian@mapzen.com',
  url='https://github.com/transitland/mapzen-gtfs',
  license='License :: OSI Approved :: MIT License',
  packages=['mzgtfs'],
  install_requires=['unicodecsv', 'mzgeohash', 'pytz'],
  zip_safe=False,
  # Include examples.
  package_data = {
    '': ['*.txt', '*.md', '*.zip']
  }
)