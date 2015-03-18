"""GTFS entities."""
import collections

def bbox(features):
  points = [s.point() for s in features]
  if not points:
    raise ValueError("Cannot create bbox with no features.")
  lons = [p[0] for p in points]
  lats = [p[1] for p in points]
  return [
    min(lons),
    min(lats),
    max(lons),
    max(lats)
  ]
  
##### Entities #####

class Entity(object):
  """A GTFS Entity.
  
  Parent-child relationships:
  
    Agency -> 
      Routes -> 
        Trips -> 
          StopTimes -> 
            Stops
  
  """
  entity_type = None

  def __init__(self, data, feed=None):
    # The row data
    self.data = data
    # Reference to GTFS Reader
    self.feed = feed
    # Relationships (e.g. trips, stop_times, ...)
    self.children = None  
    self.parents = None
  
  def __getitem__(self, key):
    # Proxy to row data
    return self.data[key]

  def get(self, key, default=None):
    """Get key."""
    try:
      return self[key]
    except KeyError:
      return default

  def name(self):
    """A reasonable display name for the entity."""
    raise NotImplementedError
    
  def feedid(self):
    """Return internal GTFS identifier."""
    return 'f-%s-%s-%s'%(
      self.feed.id(),
      self.entity_type,
      self.id()
    )
  
  def point(self):
    """Return a point geometry for this entity."""
    raise NotImplementedError  
    
  def bbox(self):
    """Return a bounding box for this entity."""
    raise NotImplementedError
  
  def geometry(self):
    """Return a GeoJSON-type geometry for this entity."""
    raise NotImplementedError
    
  # Relationships
  def pclink(self, parent, child):
    if parent.children is None:
      parent.children = set()
    if child.parents is None:
      child.parents = set()
    parent.children.add(child)
    child.parents.add(parent)
    
  # Children
  def add_child(self, child):
    self.pclink(self, child)
    
  def get_children(self):
    """Return trips for this route."""
    if self.children is not None:
      return self.children
    self.children = self._read_children()
    return self.children
    
  def _read_children(self):
    return set()
  
  # Parents
  def add_parent(self, parent):
    self.pclink(parent, self)
    
  def get_parents(self):
    if self.parents is not None:
      return self.parents
    self.parents = self._read_parents()
    return self.parents
    
  def _read_parents(self):
    return set()

class Agency(Entity):
  entity_type = 'o'
  
  """GTFS Agency."""
  def name(self):
    return self['agency_name']

  def id(self):
    return self.get('agency_id') or self.get('agency_name')

  def point(self):
    bbox = self.bbox()
    return [
      (bbox[0]+bbox[2])/2,
      (bbox[1]+bbpx[3])/2      
    ]

  def bbox(self):
    return bbox(self.stops())

  def geojson(self):
    return {
      'type': 'FeatureCollection',
      'name': self.name(),
      'properties': self.data,
      'bbox': self.bbox(),
      'geometry': self.geometry(),
      'routes': [r.geojson() for r in self.routes()],
      'features': [s.geojson() for s in self.stops()]
    }

  def geometry(self):
    b = self.bbox()
    return {
      'type': 'Polygon',
      'coordinates': [[
        [b[0], b[1]],
        [b[0], b[3]],
        [b[2], b[3]],
        [b[2], b[1]],
        [b[0], b[1]]
    ]]}

  # Agency methods.
  def preload(self):
    """Pre-load routes, trips, stops, etc."""
    # First, load all routes.
    routes_by_id = {}
    for route in self.routes():
      routes_by_id[route.id()] = route
      # Set children & parents directly.
      route.children = set()
      route.add_parent(self)
    # Second, load all trips.
    trips_by_id = {}
    for trip in self.feed.readiter('trips'):
      if trip['route_id'] in routes_by_id:
        trips_by_id[trip.id()] = trip
        # set directly
        trip.children = set()
        trip.add_parent(routes_by_id[trip['route_id']])
    # Third, load all stops...
    stops_by_id = {}
    for stop in self.feed.readiter('stops'):
      stops_by_id[stop.id()] = stop
    # Finally, load stop_times.
    for stop_time in self.feed.readiter('stop_times'):
      if stop_time['trip_id'] in trips_by_id:
        # set directly
        stop_time.add_child(stops_by_id[stop_time['stop_id']])
        stop_time.add_parent(trips_by_id[stop_time['trip_id']])

  # Agency routes.
  routes = lambda self:self.get_children()
  def _read_children(self):
    # Are we the only agency in the feed?
    check = lambda r:True
    if len(self.feed.agencies()) > 1:
      check = lambda r:(r.get('agency_id') == self.id())
    # Get the routes...    
    return set(
      filter(check, self.feed.readiter('routes'))
    )
  
  # Agency full data.
  def trips(self):
    """Return all trips for this agency."""
    trips = set()
    for route in self.routes():
      trips |= route.trips()
    return trips
    
  def stop_times(self):
    """Return all stop_times for this agency."""
    stop_times = set()
    for trip in self.trips():
      stop_times |= trip.stop_times()
    return stop_times
    
  def stops(self):
    """Return all stops visited by trips for this agency."""
    stops = set()
    for stop_time in self.stop_times():
      stops |= stop_time.stops()
    return stops
        
class Route(Entity):
  entity_type = 'r'
  
  """GTFS Route."""
  def name(self):
    return self.get('route_short_name') or self.get('route_long_name')

  def id(self):
    return self['route_id']

  def bbox(self):
    return bbox(self.stops())

  def geojson(self):
    return {
      'type': 'Feature',
      'name': self.name(),
      'properties': self.data,
      'bbox': self.bbox(),
      'geometry': self.geometry()
    }

  def geometry(self):
    # Return a line for most popular stop pattern in each direction_id.
    d0 = collections.defaultdict(int)
    d1 = collections.defaultdict(int)
    for trip in self.trips():
      seq = tuple(trip.stop_sequence())
      if trip.get('direction_id') == '1':
        d1[seq] += 1
      else:
        d0[seq] += 1
    # Sort        
    route0 = []
    if d0:
      route0 = sorted(d0.items(), key=lambda x:x[1])[-1][0]
    route1 = []
    if d1:
      route1 = sorted(d1.items(), key=lambda x:x[1])[-1][0]
    return {
      'type':'MultiLineString',
      'coordinates': [
        [stop.point() for stop in route0],
        [stop.point() for stop in route1],
      ]
    }
  
  # Trips
  trips = lambda self:self.get_children()
  def _read_children(self):
    return set([
      trip for trip
      in self.feed.readiter('trips')
      if trip.get('route_id') == self.id()
    ])

  # Serves
  def stops(self):
    """Return stops served by this route."""
    serves = set()
    for trip in self.trips():
      for stop_time in trip.stop_times():
        serves |= stop_time.stops()
    return serves
    
class Trip(Entity):
  entity_type = 't'
  
  def id(self):
    return self['trip_id']
  
  # Stop times
  stop_times = lambda self:self.get_children()
  def _read_children(self):
    """Return stop_times for this trip."""
    return set([
      stop_time for stop_time
      in self.feed.readiter('stop_times')
      if stop_time.get('trip_id') == self.id()
    ])
    
  def stop_sequence(self):
    return sorted(
      self.stop_times(), 
      key=lambda x:int(x.get('stop_sequence'))
    )

class Stop(Entity):  
  entity_type = 's'

  def id(self):
    return self['stop_id']

  def name(self):
    return self['stop_name']
    
  def point(self):
    if 'stop_lon' not in self.data or 'stop_lat' not in self.data:
      raise ValueError("Point is missing geometry.")
    return float(self.data['stop_lon']), float(self.data['stop_lat'])

  def bbox(self):
    c = self.point()
    return [c[0], c[1], c[0], c[1]]

  def geojson(self):
    return {
      'type': 'Feature',
      'name': self.name(),
      'properties': self.data,
      'bbox': self.bbox(),
      'geometry': self.geometry()
    }
  
  def geometry(self):
    return {
      "type": 'Point',
      "coordinates": self.point(),
    }

  # Routes
  def routes(self):
    serves = set()
    for stop_time in self.parents:
      for trip in stop_time.parents:
        serves |= trip.parents
    return serves

class StopTime(Entity):
  """GTFS stop_time."""

  def stops(self):
    return self.children
    
  def point(self):
    # Ugly hack.
    return list(self.children)[0].point()

class Station(Entity):
  """A grouping of related stops."""
  pass
