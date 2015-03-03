"""GTFS unit tests."""
import unittest
import os
import json

import reader

class TestReader(unittest.TestCase):
  test_gtfs = os.path.join('examples', 'sample-feed.zip')
  
  def test_readcsv(self):
    expect = {
      'stop_lat': '36.425288', 
      'zone_id': '', 
      'stop_lon': '-117.133162', 
      'stop_url': '', 
      'stop_id': 'FUR_CREEK_RES', 
      'stop_desc': '', 
      'stop_name': 'Furnace Creek Resort (Demo)'
    }
    f = reader.Reader(self.test_gtfs)
    stops = f.readcsv('stops.txt')
    found = filter(lambda x:x['stop_id'] == expect['stop_id'], stops)[0]
    for k in expect:
      assert expect[k] == found[k]
    
if __name__ == '__main__':
    unittest.main()