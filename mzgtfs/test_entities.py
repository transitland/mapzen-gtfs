"""Entity unit tests."""
import unittest
import os
import json

import reader
import entities

class TestAgency(unittest.TestCase):
  test_gtfs = os.path.join('examples', 'sample-feed.zip')

  def test_from_geojson(self):
    agency = reader.Reader(self.test_gtfs).agencies()[0]
    agency2 = entities.Agency.from_geojson(agency.geojson())
    assert json.dumps(agency.geojson(), sort_keys=True) == json.dumps(agency2.geojson(), sort_keys=True)

class TestStop(unittest.TestCase):
  test_gtfs = os.path.join('examples', 'sample-feed.zip')

  def test_from_geojson(self):
    stop = reader.Reader(self.test_gtfs).stops()[0]
    stop2 = entities.Stop.from_geojson(stop.geojson())
    assert json.dumps(stop.geojson(), sort_keys=True) == json.dumps(stop2.geojson(), sort_keys=True)

if __name__ == '__main__':
    unittest.main()