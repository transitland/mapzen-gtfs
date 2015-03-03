from distutils.core import setup

import mzgtfs

setup(
  name='mzgtfs',
  version=mzgtfs.__version__,
  description='Mapzen GTFS',
  author='Ian Rees',
  author_email='ian@mapzen.com',
  url='http://mapzen.com/',
  license='License :: OSI Approved :: MIT License',
  packages=['mzgtfs']
)