"""Entity unit tests."""
import unittest
import os
import json

import reader
import entities

class TestAgency(unittest.TestCase):
  test_gtfs = os.path.join('examples', 'sample-feed.zip')

class TestStop(unittest.TestCase):
  test_gtfs = os.path.join('examples', 'sample-feed.zip')

if __name__ == '__main__':
    unittest.main()