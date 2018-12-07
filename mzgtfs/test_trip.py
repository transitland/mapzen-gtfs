import unittest

from . import feed
from . import entities
from . import util
    
class TestTrip(unittest.TestCase):
  expect = {
    'route_id': 'CITY', 
    'trip_headsign': '', 
    'block_id': '', 
    'direction_id': '1', 
    'shape_id': '',
    'trip_id': 'CITY2', 
    'service_id': 'FULLW'
  }
  
  def test_stop_times(self):
    agency = util.preload_agency()
    entity = agency.trip(self.expect['trip_id'])
    assert len(entity.stop_times()) == 5

  def test_stop_sequence(self):
    agency = util.preload_agency()
    entity = agency.trip(self.expect['trip_id'])
    stop_sequence = entity.stop_sequence()
    assert len(stop_sequence) == 5
    expect = ['1', '2', '3', '4', '5']
    for i,j in zip(stop_sequence, expect):
      assert i.get('stop_sequence') == j
