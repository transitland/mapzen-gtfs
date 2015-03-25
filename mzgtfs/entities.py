"""GTFS entities."""
import collections

import geom

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
    """Row data from DictReader, and reference to feed."""
    # The row data
    self.data = data
    # Reference to GTFS Reader
    self.feed = feed
    # Relationships (e.g. trips, stop_times, ...)
    self.children = None  
    self.parents = None
  
  def __getitem__(self, key):
    """Proxy to row data."""
    return getattr(self.data, key)

  def get(self, key, default=None):
    """Get row data by key."""
    try:
      return self[key]
    except AttributeError:
      return default

  def name(self):
    """A reasonable display name for the entity."""
    raise NotImplementedError
      
  def point(self):
    """Return a point geometry for this entity."""
    raise NotImplementedError  
    
  def bbox(self):
    """Return a bounding box for this entity."""
    raise NotImplementedError
  
  def geometry(self):
    """Return a GeoJSON-type geometry for this entity."""
    raise NotImplementedError
    
  def feedid(self, feedid):
    """Return an identifier for a GTFS entity."""
    return 'f-%s-%s-%s'%(
      feedid,
      self.entity_type,
      self.id()
    )
    
  # Relationships
  def pclink(self, parent, child):
    """Create a parent-child relationship."""
    if parent.children is None:
      parent.children = set()
    if child.parents is None:
      child.parents = set()
    parent.children.add(child)
    child.parents.add(parent)
    
  # Children
  def add_child(self, child):
    """Add a child relationship."""
    self.pclink(self, child)
    
  def get_children(self):
    """Read and cache children."""
    if self.children is not None:
      return self.children
    self.children = self._read_children()
    return self.children
    
  def _read_children(self):
    """Read children from GTFS feed."""
    return set()
  
  # Parents
  def add_parent(self, parent):
    """Add a parent relationship."""
    self.pclink(parent, self)
    
  def get_parents(self):
    """Read and cache parents."""
    if self.parents is not None:
      return self.parents
    self.parents = self._read_parents()
    return self.parents
    
  def _read_parents(self):
    """Read the parents from the GTFS feed."""
    return set()

class Agency(Entity):
  """GTFS Agency Entity."""
  entity_type = 'o'
  
  def name(self):
    return self.get('agency_name')

  def id(self):
    return self.get('agency_id') or self.get('agency_name')

  def point(self):
    bbox = self.bbox()
    return [
      (bbox[0]+bbox[2])/2,
      (bbox[1]+bbox[3])/2      
    ]

  def bbox(self):
    return geom.bbox(self.stops())

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
    hull = geom.convex_hull(self.stops())
    return {
      'type': 'Polygon',
      'coordinates': [
        hull + [hull[0]]
      ]
    }    

  # Agency methods.
  @classmethod
  def from_json(cls, filename):
    """Load from a GeoJSON representation of agency."""
    with open(filename) as f:
      data = json.load(f)
    agency = cls()
    raise NotImplementedError
    return agency

  def preload(self):
    """Pre-load routes, trips, stops, etc."""
    # First, load all routes.
    print 'preload...'
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
    print '...done'
  
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
  """GTFS Route Entity."""
  entity_type = 'r'
  
  def name(self):
    return self.get('route_short_name') or self.get('route_long_name')

  def id(self):
    return self.get('route_id')

  def bbox(self):
    return geom.bbox(self.stops())

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
  """GTFS Trip Entity."""
  entity_type = 't'
  
  def id(self):
    return self.get('trip_id')
  
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
    """Return the sorted StopTimes for this trip."""
    return sorted(
      self.stop_times(), 
      key=lambda x:int(x.get('stop_sequence'))
    )

class Stop(Entity):  
  """GTFS Stop Entity."""
  entity_type = 's'

  def id(self):
    return self.get('stop_id')

  def name(self):
    return self.get('stop_name')
    
  def point(self):
    return float(self.get('stop_lon')), float(self.get('stop_lat'))

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
  """GTFS Stop Time Entity."""

  def stops(self):
    return self.children
    
  def point(self):
    # Ugly hack.
    return list(self.children)[0].point()
