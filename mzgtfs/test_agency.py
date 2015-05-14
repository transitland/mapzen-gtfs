import unittest
import collections
import json

import feed
import entities
import util

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
    assert agency.feedid('test') == 'gtfs://test/o/DTA'

  # Must get from Feed for remaining tests...
  def test_point(self):
    agency = util.preload_agency()
    point = agency.point()
    expect = [-116.76705100000001, 36.670485]
    for i,j in zip(point, expect):
      self.assertAlmostEqual(i,j)
    self.assertAlmostEqual(point[0], expect[0])
    self.assertAlmostEqual(point[1], expect[1])
    
  def test_bbox(self):
    agency = util.preload_agency()
    expect = [-117.133162, 36.425288, -116.40094, 36.915682]
    for i,j in zip(agency.bbox(), expect):
      self.assertAlmostEqual(i,j)
  
  def test_geometry(self):
    agency = util.preload_agency()
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
    agency = util.preload_agency()
    data = agency.json()
    assert data['name'] == 'Demo Transit Authority'
    assert 'geometry' in data
    assert 'bbox' in data
    assert len(data['features']) == 9
    # Round trip
    assert json.loads(json.dumps(data)) 
  
  def test_routes(self):
    agency = util.preload_agency()
    assert len(agency.routes()) == 5
  
  def test_route(self):
    agency = util.preload_agency()
    assert agency.route('AB')
    
  def test_trips(self):
    agency = util.preload_agency()
    assert len(agency.trips()) == 11
  
  def test_trip(self):
    agency = util.preload_agency()
    assert agency.trip('AB1')
    
  def test_stops(self):
    agency = util.preload_agency()
    assert len(agency.stops()) == 9
    
  def test_stop(self):
    agency = util.preload_agency()
    assert agency.stop('NANAA')
    
  def test_stop_times(self):
    agency = util.preload_agency()
    assert len(agency.stop_times()) == 28
    