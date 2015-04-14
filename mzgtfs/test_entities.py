"""Entity unit tests."""
import unittest
import os
import json
import collections
import copy

import feed
import entities
import util

def preload_agency(**kw):
  agency_id = kw.pop('agency_id', 'DTA')
  f = feed.Feed(util.example_feed(**kw))
  agency = f.agency(agency_id)
  agency.preload()
  return agency

class TestEntity(unittest.TestCase):
  """Test Entity methods, and unimplemented abstract methods."""
  expect = collections.OrderedDict({
    'foo':'bar',
    'rab':'oof'
  })

  def test_init(self):
    agency = entities.Entity(**self.expect)
  
  def test_get(self):
    agency = entities.Entity(**self.expect)
    for key in self.expect.keys():
      assert agency.get(key) == self.expect.get(key)
      assert agency[key] == self.expect[key]

  def test_get_keyerror(self):
    agency = entities.Entity(**self.expect)    
    with self.assertRaises(KeyError):
      agency['asdf']
  
  def test_get_default(self):
    agency = entities.Entity(**self.expect)    
    assert agency.get('asdf','test') == 'test'
    
  def test_get_namedtuple(self):
    nt = collections.namedtuple('test', self.expect.keys())
    agency = entities.Entity.from_row(nt(**self.expect))
    for key in self.expect.keys():
      assert agency.get(key) == self.expect.get(key)
      assert agency[key] == self.expect[key]

  def test_get_namedtuple_keyerror(self):
    nt = collections.namedtuple('test', self.expect.keys())
    agency = entities.Entity.from_row(nt(**self.expect))
    with self.assertRaises(KeyError):
      agency['asdf']

  def test_setitem(self):
    agency = entities.Entity(**self.expect)
    agency['test'] = 'ok'
    assert agency['test'] == 'ok'
  
  def test_setitem_ntconvert(self):
    nt = collections.namedtuple('test', self.expect.keys())
    agency = entities.Entity.from_row(nt(**self.expect))
    agency['test'] = 'ok'
    assert agency['test'] == 'ok'    

  def test_name(self):
    entity = entities.Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.name()

  def test_id(self):
    entity = entities.Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.id()

  def test_point(self):
    entity = entities.Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.point()

  def test_bbox(self):
    entity = entities.Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.bbox()

  def test_geometry(self):
    entity = entities.Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.geometry()

  def test_from_json(self):
    with self.assertRaises(NotImplementedError):
      entities.Entity.from_json(self.expect)

  def test_json(self):
    entity = entities.Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.json()

  # Relationships
  def test_pclink(self):
    agency1 = entities.Entity(**self.expect)    
    agency2 = entities.Entity(**self.expect)    
    agency1.pclink(agency1, agency2)
    assert agency2 in agency1.get_children()
    assert agency1 in agency2.get_parents()

  def test_add_child(self):
    agency1 = entities.Entity(**self.expect)    
    agency2 = entities.Entity(**self.expect)    
    agency1.add_child(agency2)
    assert agency2 in agency1.get_children()
    assert agency1 in agency2.get_parents()

  def test_add_parent(self):
    agency1 = entities.Entity(**self.expect)    
    agency2 = entities.Entity(**self.expect)    
    agency2.add_parent(agency1)
    assert agency2 in agency1.get_children()
    assert agency1 in agency2.get_parents()

  def test_get_parents(self):
    self.test_add_parent()
    entity = entities.Entity(**self.expect)    
    assert not entity.get_parents()
  
  def test_get_children(self):
    self.test_add_child()
    entity = entities.Entity(**self.expect)    
    assert not entity.get_children()
    
  def test__read_children(self):
    entity = entities.Entity(**self.expect)
    assert not entity._read_children()
    
  def test__read_parents(self):
    entity = entities.Entity(**self.expect)
    assert not entity._read_parents()
    
class TestAgency(unittest.TestCase):
  """Test Agency."""
  expect = collections.OrderedDict({
    'agency_url': 'http://google.com', 
    'agency_name': 'Demo Transit Authority', 
    'agency_id': 'DTA', 
    'agency_timezone': 'America/Los_Angeles'
  })

  def test_name(self):
    agency = entities.Agency(**self.expect)    
    assert agency.name() == self.expect['agency_name']
    
  def test_id(self):
    agency = entities.Agency(**self.expect)    
    assert agency.id() == self.expect['agency_id']
    
  def test_feedid(self):    
    agency = entities.Agency(**self.expect)    
    assert agency.feedid('f-test') == 'f-test-o-DTA'

  def test__read_parents(self):
    # empty set
    agency = preload_agency()
    assert not agency._read_parents()

  def test__read_children(self):
    # check for 5 child routes
    agency = preload_agency()
    assert len(agency._read_children()) == 5
    
  def test__read_children_multipleagencies(self):
    agency = preload_agency(
      feed='sample-feed-multipleagencies.zip', 
      agency_id='ATD'
    )
    assert len(agency._read_children()) == 0

  # Must get from Feed for remaining tests...
  def test_point(self):
    agency = preload_agency()
    point = agency.point()
    expect = [-116.76705100000001, 36.670485]
    for i,j in zip(point, expect):
      self.assertAlmostEqual(i,j)
    self.assertAlmostEqual(point[0], expect[0])
    self.assertAlmostEqual(point[1], expect[1])
    
  def test_bbox(self):
    agency = preload_agency()
    expect = [-117.133162, 36.425288, -116.40094, 36.915682]
    for i,j in zip(agency.bbox(), expect):
      self.assertAlmostEqual(i,j)
  
  def test_geometry(self):
    agency = preload_agency()
    geometry = agency.geometry()
    # a beast...
    expect = [
      (-117.133162, 36.425288), 
      (-116.40094, 36.641496), 
      (-116.751677, 36.915682), 
      (-116.76821, 36.914893), 
      (-116.81797, 36.88108),
      (-117.133162, 36.425288)
    ]
    assert geometry['type'] == 'Polygon'
    for i,j in zip(geometry['coordinates'][0], expect):
      self.assertAlmostEqual(i[0],j[0])
      self.assertAlmostEqual(i[1],j[1])
  
  def test_json(self):
    # Basic checks for JSON sanity.
    agency = preload_agency()
    data = agency.json()
    assert data['name'] == 'Demo Transit Authority'
    assert 'geometry' in data
    assert 'bbox' in data
    assert len(data['features']) == 9
    # Round trip
    assert json.loads(json.dumps(data)) 
  
  def test_routes(self):
    agency = preload_agency()
    assert len(agency.routes()) == 5
  
  def test_route(self):
    agency = preload_agency()
    assert agency.route(id='AB')
    
  def test_trips(self):
    agency = preload_agency()
    assert len(agency.trips()) == 11
  
  def test_trip(self):
    agency = preload_agency()
    assert agency.trip('AB1')
    
  def test_stops(self):
    agency = preload_agency()
    assert len(agency.stops()) == 9
    
  def test_stop(self):
    agency = preload_agency()
    assert agency.stop('NANAA')
    
  def test_stop_times(self):
    agency = preload_agency()
    assert len(agency.stop_times()) == 28
    
class TestRoute(unittest.TestCase):  
  expect = {
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

  def test_name(self):
    # Test name
    entity = entities.Route(**self.expect)    
    assert entity.name() == self.expect['route_short_name']
    # Test fallback
    expect = copy.copy(self.expect)
    expect.pop('route_short_name')
    entity = entities.Route(**expect)    
    assert entity.name() == self.expect['route_long_name']
    
  def test_id(self):
    entity = entities.Route(**self.expect)
    assert entity.id() == self.expect['route_id']
  
  # Requires preload
  def test_bbox(self):
    agency = preload_agency()
    route = agency.route(self.expect['route_id'])
    expect = [-116.81797, 36.868446, -116.784582, 36.88108]
    for i,j in zip(route.bbox(), expect):
      self.assertAlmostEqual(i,j)
  
  def test_json(self):
    agency = preload_agency()
    entity = agency.route(self.expect['route_id'])
    data = entity.json()
    assert data['name'] == entity.name()
    assert data['type'] == 'Feature'
    assert data['geometry']['type'] == 'MultiLineString'
    # Round trip
    assert json.loads(json.dumps(data)) 

  def test_geometry(self):
    agency = preload_agency()
    route = agency.route(self.expect['route_id'])
    geometry = route.geometry()
    assert geometry['type'] == 'MultiLineString'
    # Line 1
    expect = [
      (-116.784582, 36.868446), 
      (-116.81797, 36.88108)]
    for i,j in zip(geometry['coordinates'][0], expect):
      self.assertAlmostEqual(i[0],j[0])
      self.assertAlmostEqual(i[1],j[1])
    # Line 2
    expect = [
      (-116.81797, 36.88108), 
      (-116.784582, 36.868446)
    ]
    for i,j in zip(geometry['coordinates'][1], expect):
      self.assertAlmostEqual(i[0],j[0])
      self.assertAlmostEqual(i[1],j[1])
    
  def test__read_children(self):
    agency = preload_agency()
    route = agency.route(self.expect['route_id'])
    assert len(route._read_children()) == 2
        
  def test_trips(self):
    agency = preload_agency()
    route = agency.route(self.expect['route_id'])
    assert len(route.trips()) == 2
    
  def test_stops(self):
    agency = preload_agency()
    route = agency.route(self.expect['route_id'])
    assert len(route.stops()) == 2
    
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
  
  def test__read_children(self):
    agency = preload_agency()
    entity = agency.trip(self.expect['trip_id'])
    assert len(entity._read_children()) == 5

  def test_stop_times(self):
    agency = preload_agency()
    entity = agency.trip(self.expect['trip_id'])
    assert len(entity.stop_times()) == 5

  def test_stop_sequence(self):
    agency = preload_agency()
    entity = agency.trip(self.expect['trip_id'])
    stop_sequence = entity.stop_sequence()
    assert len(stop_sequence) == 5
    expect = ['1', '2', '3', '4', '5']
    for i,j in zip(stop_sequence, expect):
      assert i.get('stop_sequence') == j

class TestStopTime(unittest.TestCase):
  def test_point(self):
    pass

  def test_stops(self):
    pass

class TestStop(unittest.TestCase):
  expect = {
    'stop_lat': '36.425288', 
    'stop_lon': '-117.133162', 
    'stop_id': 'FUR_CREEK_RES', 
    'stop_name': 'Furnace Creek Resort (Demo)'
  }
    
  def test_id(self):
    entity = entities.Stop(**self.expect)
    assert entity.id() == self.expect['stop_id']

  def test_name(self):
    entity = entities.Stop(**self.expect)    
    assert entity.name() == self.expect['stop_name']

  def test_point(self):
    entity = entities.Stop(**self.expect)    
    expect = (-117.133162, 36.425288)
    for i,j in zip(entity.point(), expect):
      self.assertAlmostEqual(i,j)

  def test_bbox(self):
    entity = entities.Stop(**self.expect)    
    expect = [-117.133162, 36.425288, -117.133162, 36.425288]
    for i,j in zip(entity.bbox(), expect):
      self.assertAlmostEqual(i,j)

  def test_json(self):
    entity = entities.Stop(**self.expect)    
    data = entity.json()
    assert data['name'] == entity.name()
    assert data['type'] == 'Feature'
    assert data['geometry']['type'] == 'Point'
    assert data['properties']
    # Round trip
    assert json.loads(json.dumps(data)) 

  def test_geometry(self):
    entity = entities.Stop(**self.expect)    
    expect = (-117.133162, 36.425288)
    geometry = entity.geometry()
    assert geometry['type'] == 'Point'
    for i,j in zip(geometry['coordinates'], expect):
      self.assertAlmostEqual(i,j)

  def test_routes(self):
    agency = preload_agency()
    entity = agency.stop(self.expect['stop_id'])
    routes = entity.routes()
    assert len(routes) == 1
    assert list(routes)[0].id() == 'BFC'
