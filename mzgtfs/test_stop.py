import unittest
import json

import feed
import entities
import util

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
    agency = util.preload_agency()
    entity = agency.stop(self.expect['stop_id'])
    routes = entity.routes()
    assert len(routes) == 1
    assert list(routes)[0].id() == 'BFC'