"""Reader unit tests."""
import unittest
import os
import json

import reader

class TestReader(unittest.TestCase):
  test_gtfs_feed = os.path.join('examples', 'sample-feed.zip')
  test_geojson_feed = os.path.join('examples', 'sample-feed.geojson')
  stop_expect = {
      'stop_lat': '36.425288', 
      'zone_id': '', 
      'stop_lon': '-117.133162', 
      'stop_url': '', 
      'stop_id': 'FUR_CREEK_RES', 
      'stop_desc': '', 
      'stop_name': 'Furnace Creek Resort (Demo)'
    }

  def test_read_stop(self):
    f = reader.Reader(self.test_gtfs_feed)
    stops = f.read('stops')
    found = filter(lambda x:x['stop_id'] == self.stop_expect['stop_id'], stops)[0]
    for k in self.stop_expect:
      assert self.stop_expect[k] == found[k]
      
if __name__ == '__main__':
    unittest.main()