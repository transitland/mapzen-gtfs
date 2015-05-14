"""GTFS Agency entity."""
import entity
import geom
import util
import validation

class Agency(entity.Entity):
  """GTFS Agency entity."""
  ENTITY_TYPE = 'o'
  KEY = 'agency_id'
  REQUIRED = [
    'agency_name',
    'agency_url',
    'agency_timezone'
  ]
  OPTIONAL = [
    'agency_id',
    'agency_lang',
    'agency_phone',
    'agency_fare_url'
  ]  
  def name(self):
    return self.get('agency_name')

  def id(self):
    # agency_id is optional.
    return self.get('agency_id') or self.get('agency_name')

  def point(self):
    bbox = self.bbox()
    return [
      (bbox[0]+bbox[2])/2,
      (bbox[1]+bbox[3])/2      
    ]

  def bbox(self):
    return geom.bbox(self.stops())

  def json(self):
    return {
      'type': 'FeatureCollection',
      'name': self.name(),
      'properties': self.data,
      'bbox': self.bbox(),
      'geometry': self.geometry(),
      'routes': [r.json() for r in self.routes()],
      'features': [s.json() for s in self.stops()]
    }

  def geometry(self):
    hull = geom.convex_hull(self.stops())
    return {
      'type': 'Polygon',
      'coordinates': [
        hull + [hull[0]]
      ]
    }    

  # Agency specific methods.
  def dates(self):
    found = set(trip.get('service_id') for trip in self.trips())
    dates = [
      date 
      for date in self._feed.read('calendar') 
      if date.get('service_id') in found
    ]
    return [
      min(date.start() for date in dates),
      max(date.end() for date in dates)
    ]
  
  # Graph.      
  def routes(self):
    """Return all routes for this agency."""
    return set(self.children()) # copy
  
  def route(self, key):
    """Return a single route by ID."""
    return util.filtfirst(self.routes(), id=key)
  
  def trips(self):
    """Return all trips for this agency."""
    trips = set()
    for route in self.routes():
      trips |= route.trips()
    return trips
  
  def trip(self, key):
    """Return a single trip by ID."""
    return util.filtfirst(self.trips(), id=key)

  def stops(self):
    """Return all stops visited by trips for this agency."""
    stops = set()
    for stop_time in self.stop_times():
      stops |= stop_time.stops()
    return stops

  def stop(self, key):
    """Return a single stop by ID."""
    return util.filtfirst(self.stops(), id=key)
    
  def stop_times(self):
    """Return all stop_times for this agency."""
    stop_times = set()
    for trip in self.trips():
      stop_times |= trip.stop_times()
    return stop_times
    
  ##### Validation #####
    
  def validate(self, validator=None):
    validator = super(Agency, self).validate(validator)
    # Required
    with validator(self): 
      assert self.get('agency_name'), \
        "Required: agency_name"
    with validator(self): 
      assert self.get('agency_url'), "Required: agency_url"
      assert validation.valid_url(self.get('agency_url')), \
        "Invalid agency_url"
    with validator(self):
      assert self.get('agency_timezone'), "Required: agency_timezone"
      assert validation.valid_tz(self.get('agency_timezone')), \
        "Invalid agency_timezone"
    # Optional
    with validator(self): 
      if self.get('agency_lang'):
        assert validation.valid_language(self.get('agency_lang')), \
          "Invalid language"
    with validator(self): 
      if self.get('agency_fare_url'):
        assert validation.valid_url(self.get('agency_fare_url')), \
          "Invalid agency_fare_url"
    with validator(self):
      if self.get('agency_id'): 
        pass
    with validator(self):
      if self.get('agency_phone'):
        pass
    return validator
