"""GTFS Route entity."""
import collections

import entity
import geom
import validation

class Route(entity.Entity):
  """GTFS Route entity."""
  ENTITY_TYPE = 'r'
  KEY = 'route_id'
  REQUIRED = [
    'route_id',
    'route_short_name',
    'route_long_name',
    'route_type'
  ]
  OPTIONAL = [
    'agency_id',
    'route_desc',
    'route_url',
    'route_color',
    'route_text_color'
  ]
  
  def name(self):
    return self.get('route_short_name') or self.get('route_long_name')

  def id(self):
    return self.get('route_id')

  def bbox(self):
    return geom.bbox(self.stops())

  def json(self):
    return {
      'type': 'Feature',
      'name': self.name(),
      'properties': self.data,
      'bbox': self.bbox(),
      'geometry': self.geometry()
    }

  def geometry(self):
    # Return a line for most popular shape_id or stop pattern
    #   in each direction_id.
    d0 = collections.defaultdict(int)
    d1 = collections.defaultdict(int)
    # Grab the shapes.
    try:
      shapes = self._feed.shapes()
    except KeyError:
      shapes = {}
    for trip in self.trips():
      if trip.get('shape_id') and trip.get('shape_id') in shapes:
        seq = tuple(shapes[trip['shape_id']].points())
      else:
        seq = tuple(i.point() for i in trip.stop_sequence())
      if int(trip.get('direction_id') or 0):
        d1[seq] += 1
      else:
        d0[seq] += 1
    # Sort to find the most popular shape.
    route0 = []
    if d0:
      route0 = sorted(d0.items(), key=lambda x:x[1])[-1][0]
    route1 = []
    if d1:
      route1 = sorted(d1.items(), key=lambda x:x[1])[-1][0]
    return {
      'type':'MultiLineString',
      'coordinates': [route0, route1]
    }

  def vehicle(self):
    return {
      '0': 'tram',
      '1': 'metro',
      '2': 'rail',
      '3': 'bus',
      '4': 'ferry',
      '5': 'cablecar',
      '6': 'gondola',
      '7': 'funicular',
      '700': 'Bus Service',
      '800': 'Trolleybus Service',
      None: None,
      '': None
    }[self.get('route_type')]

  # Graph.
  def trips(self):
    """Return trips for this route."""
    return set(self.children()) # copy

  def stops(self):
    """Return stops served by this route."""
    serves = set()
    for trip in self.trips():
      for stop_time in trip.stop_times():
        serves |= stop_time.stops()
    return serves

  ##### Validation #####
  def validate(self, validator=None):
    validator = super(Route, self).validate(validator)
    # Required
    with validator(self):
      assert self.get('route_id'), "Required: route_id"
    with validator(self):
      assert self.get('route_type'), "Required: route_type"
      assert self.vehicle(), "Invalid route_type"
    with validator(self):
      assert self.get('route_short_name') or self.get('route_long_name'), \
        "Must provide either route_short_name or route_long_name"
    # TODO: Warnings:
    #   short name too long
    #   short name == long name
    #   route_desc != route name
    # Optional
    with validator(self):
      if self.get('agency_id'): pass
    with validator(self):
      if self.get('route_desc'): pass
    with validator(self):
      if self.get('route_url'):
        assert validation.valid_url(self.get('route_url')), \
          "Invalid route_url"
    with validator(self):
      if self.get('route_color'):
        assert validation.valid_color(self.get('route_color')), \
          "Invalid route_color"
    with validator(self):
      if self.get('route_text_color'):
        assert validation.valid_color(self.get('route_text_color')), \
          "Invalid route_text_color"
    return validator
