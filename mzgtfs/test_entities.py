"""Entity unit tests."""
import unittest
import os
import json
import collections

import feed
import entities

class TestEntity(unittest.TestCase):
  """Test Entity methods, and unimplemented abstract methods."""
  data = collections.OrderedDict({
    'foo':'bar',
    'rab':'oof'
  })

  def test_init(self):
    agency = entities.Entity(self.data)
  
  def test_get(self):
    agency = entities.Entity(self.data)
    for key in self.data.keys():
      assert agency.get(key) == self.data.get(key)
      assert agency[key] == self.data[key]

  def test_get_keyerror(self):
    agency = entities.Entity(self.data)    
    with self.assertRaises(KeyError):
      agency['asdf']
  
  def test_get_default(self):
    agency = entities.Entity(self.data)    
    assert agency.get('asdf','test') == 'test'
    
  def test_get_namedtuple(self):
    nt = collections.namedtuple('test', self.data.keys())
    agency = entities.Entity(nt(**self.data))
    for key in self.data.keys():
      assert agency.get(key) == self.data.get(key)
      assert agency[key] == self.data[key]

  def test_get_namedtuple_keyerror(self):
    nt = collections.namedtuple('test', self.data.keys())
    agency = entities.Entity(nt(**self.data))
    with self.assertRaises(KeyError):
      agency['asdf']

  def test_name(self):
    entity = entities.Entity(self.data)
    with self.assertRaises(NotImplementedError):
      entity.name()

  def test_id(self):
    entity = entities.Entity(self.data)
    with self.assertRaises(NotImplementedError):
      entity.id()

  def test_point(self):
    entity = entities.Entity(self.data)
    with self.assertRaises(NotImplementedError):
      entity.point()

  def test_bbox(self):
    entity = entities.Entity(self.data)
    with self.assertRaises(NotImplementedError):
      entity.bbox()

  def test_geometry(self):
    entity = entities.Entity(self.data)
    with self.assertRaises(NotImplementedError):
      entity.geometry()

  def test_from_json(self):
    with self.assertRaises(NotImplementedError):
      entity = entities.Entity.from_json(self.data)

  def test_json(self):
    entity = entities.Entity(self.data)
    with self.assertRaises(NotImplementedError):
      entity.json()

  # Relationships
  def test_pclink(self):
    agency1 = entities.Entity(self.data)    
    agency2 = entities.Entity(self.data)    
    agency1.pclink(agency1, agency2)
    assert agency2 in agency1.get_children()
    assert agency1 in agency2.get_parents()

  def test_add_child(self):
    agency1 = entities.Entity(self.data)    
    agency2 = entities.Entity(self.data)    
    agency1.add_child(agency2)
    assert agency2 in agency1.get_children()
    assert agency1 in agency2.get_parents()

  def test_add_parent(self):
    agency1 = entities.Entity(self.data)    
    agency2 = entities.Entity(self.data)    
    agency2.add_parent(agency1)
    assert agency2 in agency1.get_children()
    assert agency1 in agency2.get_parents()

  def test_get_parents(self):
    self.test_add_parent()
    entity = entities.Entity(self.data)    
    assert not entity.get_parents()
  
  def test_get_children(self):
    self.test_add_child()
    entity = entities.Entity(self.data)    
    assert not entity.get_children()
    
  def test__read_children(self):
    entity = entities.Entity(self.data)
    assert not entity._read_children()
    
  def test__read_parents(self):
    entity = entities.Entity(self.data)
    assert not entity._read_parents()
    
class TestAgency(unittest.TestCase):
  """Test Agency."""
  test_gtfs_feed = os.path.join('examples', 'sample-feed.zip')
  data = collections.OrderedDict({
    'agency_url': 'http://google.com', 
    'agency_name': 'Demo Transit Authority', 
    'agency_id': 'DTA', 
    'agency_timezone': 'America/Los_Angeles'
  })

  def _preload(self):
    f = feed.Feed(self.test_gtfs_feed)
    agency = f.agency(self.data['agency_id'])
    agency.preload()
    return agency
  
  def test_name(self):
    agency = entities.Agency(self.data)    
    assert agency.name() == self.data['agency_name']
    
  def test_id(self):
    agency = entities.Agency(self.data)    
    assert agency.id() == self.data['agency_id']
    
  def test_feedid(self):    
    agency = entities.Agency(self.data)    
    assert agency.feedid('f-test') == 'f-test-o-DTA'

  def test__read_parents(self):
    # empty set
    agency = self._preload()
    assert not agency._read_parents()

  def test__read_children(self):
    # check for 5 child routes
    agency = self._preload()
    assert len(agency._read_children()) == 5

  # Must get from Feed for remaining tests...
  def test_point(self):
    agency = self._preload()
    point = agency.point()
    expect = [-116.76705100000001, 36.670485]
    for i,j in zip(point, expect):
      self.assertAlmostEqual(i,j)
    self.assertAlmostEqual(point[0], expect[0])
    self.assertAlmostEqual(point[1], expect[1])
    
  def test_bbox(self):
    agency = self._preload()
    bbox = agency.bbox()
    expect = [-117.133162, 36.425288, -116.40094, 36.915682]
    for i,j in zip(bbox, expect):
      self.assertAlmostEqual(i,j)
  
  def test_geometry(self):
    agency = self._preload()
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
    agency = self._preload()
    data = agency.json()
    assert data['name'] == 'Demo Transit Authority'
    assert 'geometry' in data
    assert 'bbox' in data
    assert len(data['features']) == 9
    # Round trip
    assert json.loads(json.dumps(data)) 
  
  def test_routes(self):
    agency = self._preload()
    assert len(agency.routes()) == 5
  
  def test_route(self):
    agency = self._preload()
    assert agency.route(id='AB')
    
  def test_trips(self):
    agency = self._preload()
    assert len(agency.trips()) == 11
  
  def test_trip(self):
    agency = self._preload()
    assert agency.trip('AB1')
    
  def test_stops(self):
    agency = self._preload()
    assert len(agency.stops()) == 9
    
  def test_stop(self):
    agency = self._preload()
    assert agency.stop('NANAA')
    
  def test_stop_times(self):
    agency = self._preload()
    assert len(agency.stop_times()) == 28
    
class TestRoute(unittest.TestCase):
  pass
    
if __name__ == '__main__':
    unittest.main()