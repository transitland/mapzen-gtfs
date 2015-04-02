"""Feed unit tests."""
import unittest
import os
import json
import inspect

import util
import feed
import entities

class TestFeed(unittest.TestCase):
  """Test Feed Reader.
  
  TODO: Test Unicode?
  
  """  
  agency_expect = {
    'agency_url': 'http://google.com', 
    'agency_name': 'Demo Transit Authority', 
    'agency_id': 'DTA', 
    'agency_timezone': 'America/Los_Angeles'
  }
  
  route_expect = {
    'route_long_name': 'Airport - Bullfrog', 
    'route_id': 'AB', 
    'route_type': '3', 
    'route_text_color': '', 
    'agency_id': 'DTA', 
    'route_color': '', 
    'route_url': '', 
    'route_desc': '', 
    'route_short_name': '10'
  }
  
  stop_expect = {
    'stop_lat': '36.425288', 
    'stop_lon': '-117.133162', 
    'stop_id': 'FUR_CREEK_RES', 
    'stop_name': 'Furnace Creek Resort (Demo)'
  }

  def test_init(self):
    f = feed.Feed(util.example_feed())
  
  def test_read(self):
    # Test basic read
    f = feed.Feed(util.example_feed())
    data = f.read('stops')
    # check we got 9 entities
    assert len(data) == 9
    # check cache
    assert 'stops' in f.cache
  
  def test_iterread(self):
    # Test generator read
    f = feed.Feed(util.example_feed())
    data = f.iterread('stops')
    assert inspect.isgenerator(data)
    assert len(list(data)) == 9

  def test_debug(self):
    f = feed.Feed(util.example_feed(), debug=True)
    data = f.read('stops')

  def test_cache(self):
    f = feed.Feed(util.example_feed())
    # Read a first time
    data1 = f.read('stops')
    # Read a second time
    data2 = f.read('stops')
    assert len(data1) == len(data2)
    assert 'stops' in f.cache
    assert len(data1) == len(f.cache['stops'])

  def test_read_invalidfile(self):
    f = feed.Feed(util.example_feed())
    with self.assertRaises(KeyError):
      f.read('invalidfile')

  def test_agencies(self):
    f = feed.Feed(util.example_feed())
    data = f.agencies()
    assert len(data) == 1
    
  def test_agency(self):
    f = feed.Feed(util.example_feed())
    data = f.agency(self.agency_expect['agency_id'])
    for k in self.agency_expect:
      assert self.agency_expect[k] == data[k]
  
  def test_routes(self):
    f = feed.Feed(util.example_feed())
    assert len(f.routes()) == 5
    
  def test_route(self):
    f = feed.Feed(util.example_feed())
    data = f.route(self.route_expect['route_id'])
    for k in self.route_expect:
      assert self.route_expect[k] == data[k]

  def test_stops(self):
    f = feed.Feed(util.example_feed())
    assert len(f.stops()) == 9

  def test_stop(self):
    f = feed.Feed(util.example_feed())
    data = f.stop(self.stop_expect['stop_id'])
    for k in self.stop_expect:
      assert self.stop_expect[k] == data[k]
