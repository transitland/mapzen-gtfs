"""GTFS entities."""
import collections
import json
import re

import mzgeohash

# Regexes
REPLACE = [
  [r'\'',''],
  [r'\.',''],
  [r' - ',':'],
  [r'&',':'],
  [r'@',':'],
  [r'\/',':'],
  [r' ','']
]
ABBR = [
  'street', 
  'st',
  'sts',
  'ctr',
  'center',
  'ave', 
  'avenue', 
  'av',
  'boulevard', 
  'blvd', 
  'road', 
  'rd', 
  'alley', 
  'aly', 
  'way', 
  'parkway', 
  'pkwy', 
  'lane',
  'ln',
  'hwy',
  'court',
  'ct',
]
REPLACE_ABBR = [[r'\b%s\b'%i, ''] for i in ABBR]

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

def geohash_features(features):
  # Filter stops without valid coordinates...
  points = [feature.point() for feature in features if feature.point()]
  if not points:
    raise Exception("Not enough points.")
  c = centroid_points(points)
  return mzgeohash.neighborsfit(c, points)
  
def centroid_points(points):
  """Return the lon,lat centroid for features."""
  # Todo: Geographic center, or simple average?
  import ogr, osr
  multipoint = ogr.Geometry(ogr.wkbMultiPoint)
  # spatialReference = osr.SpatialReference() ...
  for point in points:
    p = ogr.Geometry(ogr.wkbPoint)
    p.AddPoint(point[1], point[0])
    multipoint.AddGeometry(p)
  point = multipoint.Centroid()
  return (point.GetY(), point.GetX())

class Entity(object):
  """A GTFS Entity.
  
  Parent-child relationships:
  
    Agency -> 
      Routes -> 
        Trips -> 
          StopTimes -> 
            Stops
  
  """
  # OnestopID prefix.
  onestop_type = None
  
  def __init__(self, data, feed=None):
    self.cache = {}
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
  
  def mangle(self, s):
    """Mangle a string into an identifier."""
    s = s.lower()
    for a,b in REPLACE:
      s = re.sub(a,b,s)
    return s    

  def onestop(self):
    """Return the OnestopID for this entity."""
    return '%s-%s-%s'%(
      self.onestop_type, 
      self.geohash(), 
      self.mangle(self.name())
    )

  def geohash(self):
    """Return the geohash for this entity."""
    raise NotImplementedError  

  def point(self):
    """Return a point geometry for this entity."""
    raise NotImplementedError  
    
  def bbox(self):
    """Return a bounding box for this entity."""
    raise NotImplementedError    
    
  def geojson(self):
    """Return a dictionary that is GeoJSON representation of entity."""
    raise NotImplementedError
    
  def from_geojson(self, d):
    """Load from GeoJSON representation."""
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
  """GTFS Agency."""
  onestop_type = 'o'

  def name(self):
    return self['agency_name']

  def geohash(self):
    return geohash_features(self.stops())

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
      'onestopId': self.onestop(),
      'geohash': self.geohash(),
      'bbox': self.bbox(),
      'routes': [r.geojson() for r in self.routes()],
      'features': [s.geojson() for s in self.stops()],
    }

  # @classmethod
  # def from_geojson(cls, d):
  #   agency = cls(d['properties'])
  #   agency.children = cls(d['routes'])
  #   return agency
    
  # Agency methods.
  def preload(self):
    """Pre-load routes, trips, stops, etc."""
    # First, load all routes.
    routes = {}
    for route in self.routes():
      routes[route['route_id']] = route
      # Set children & parents directly.
      route.children = set()
      route.add_parent(self)
    # Second, load all trips.
    trips = {}
    for trip in self.feed.readiter('trips'):
      if trip['route_id'] in routes:
        trips[trip['trip_id']] = trip
        # set directly
        trip.children = set()
        trip.add_parent(routes[trip['route_id']])
    # Third, load all stops...
    stops = {}
    for stop in self.feed.readiter('stops'):
      stops[stop['stop_id']] = stop
    # Finally, load stop_times.
    for stop_time in self.feed.readiter('stop_times'):
      if stop_time['trip_id'] in trips:
        # set directly
        stop_time.add_child(stops[stop_time['stop_id']])
        stop_time.add_parent(trips[stop_time['trip_id']])

  # Agency routes.
  routes = lambda self:self.get_children()
  def _read_children(self):
    # Are we the only agency in the feed?
    check = lambda r:True
    if len(self.feed.agencies()) > 1:
      check = lambda r:(r.get('agency_id') == self.get('agency_id'))
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
  """GTFS Route."""
  onestop_type = 'r'
  
  def name(self):
    return self.get('route_short_name') or self.get('route_long_name')

  def geohash(self):
    return geohash_features(self.stops())

  def geojson(self):
    return {
      'type': 'Feature',
      'name': self.name(),
      'properties': self.data,
      'onestopId': self.onestop(),
      'serves': [stop.onestop() for stop in self.stops()],
      'geohash': self.geohash(),
      'bbox': self.bbox(),
      'geometry': self._geometry()
    }
    
  def bbox(self):
    return bbox(self.stops())
  
  def _geometry(self):
    """Get a GeoJSON geometry that represents most common stop patterns."""
    # Return a line for most popular stop pattern in each direction_id.
    d0 = collections.defaultdict(int)
    d1 = collections.defaultdict(int)
    for trip in self.trips():
      seq = tuple(trip.stop_sequence())
      if trip.get('direction_id') == '1':
        d1[seq] += 1
      else:
        d0[seq] += 1
        
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
      if trip.get('route_id') == self['route_id']
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
  onestop_type = 't'
  
  # Stop times
  stop_times = lambda self:self.get_children()
  def _read_children(self):
    """Return stop_times for this trip."""
    return set([
      stop_time for stop_time
      in self.feed.readiter('stop_times')
      if stop_time.get('trip_id') == self['trip_id']
    ])
    
  def stop_sequence(self):
    return sorted(
      self.stop_times(), 
      key=lambda x:int(x.get('stop_sequence'))
    )

class Stop(Entity):
  onestop_type = 's'

  def name(self):
    return self['stop_name']
    
  def mangle(self,s ):
    """Also replace common road abbreviations."""
    s = s.lower()
    for a,b in REPLACE:
      s = re.sub(a,b,s)
    for a,b in REPLACE_ABBR:
      s = re.sub(a,b,s)
    return s    

  def geohash(self):
    """Return 10 characters of geohash."""
    return mzgeohash.encode(self.point())[:10]
    
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
      'onestopId': self.onestop(),
      'serves': [route.onestop() for route in self.routes()],
      'geohash': self.geohash(),
      'bbox': self.bbox(),
      'geometry': {
        "type": 'Point',
        "coordinates": self.point(),
      }
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
