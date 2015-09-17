import unittest
import json
import copy

import feed
import entities
import util

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
    agency = util.preload_agency()
    route = agency.route(self.expect['route_id'])
    expect = [-116.81797, 36.868446, -116.784582, 36.88108]
    for i,j in zip(route.bbox(), expect):
      self.assertAlmostEqual(i,j)

  def test_json(self):
    agency = util.preload_agency()
    entity = agency.route(self.expect['route_id'])
    data = entity.json()
    assert data['name'] == entity.name()
    assert data['type'] == 'Feature'
    assert data['geometry']['type'] == 'MultiLineString'
    # Round trip
    assert json.loads(json.dumps(data))

  def test_geometry(self):
    agency = util.preload_agency()
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

  def test_trips(self):
    agency = util.preload_agency()
    route = agency.route(self.expect['route_id'])
    assert len(route.trips()) == 2

  def test_stops(self):
    agency = util.preload_agency()
    route = agency.route(self.expect['route_id'])
    assert len(route.stops()) == 2

    
