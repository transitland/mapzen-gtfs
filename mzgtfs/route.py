"""GTFS Route entity."""
import collections

import entity
import geom

class Route(entity.Entity):
  """GTFS Route entity."""
  entity_type = 'r'
  
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
      None: None,
      '': None
    }[self.get('route_type')]
  
  # Graph.
  def _read_children(self):
    """Children: Trips"""
    return set([
      trip for trip
      in self._feed.iterread('trips')
      if trip.get('route_id') == self.id()
    ])

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
