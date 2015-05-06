"""GTFS Agency entity."""
import pytz

import entity
import geom
import util
import iso639

class Agency(entity.Entity):
  """GTFS Agency entity."""
  entity_type = 'o'
  
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
  def preload(self):
    """Pre-load routes, trips, stops, etc."""
    # First, load all routes.
    routes_by_id = {}
    for route in self.routes():
      routes_by_id[route.id()] = route
      # Set children & parents directly.
      route._children = set()
      route.add_parent(self)
    # Second, load all trips.
    trips_by_id = {}
    for trip in self._feed.iterread('trips'):
      if trip['route_id'] in routes_by_id:
        trips_by_id[trip.id()] = trip
        # set directly
        trip._children = set()
        trip.add_parent(routes_by_id[trip['route_id']])
    # Third, load all stops...
    stops_by_id = {}
    for stop in self._feed.iterread('stops'):
      stops_by_id[stop.id()] = stop
    # Finally, load stop_times.
    for stop_time in self._feed.iterread('stop_times'):
      if stop_time['trip_id'] in trips_by_id:
        # set directly
        stop_time.add_child(stops_by_id[stop_time['stop_id']])
        stop_time.add_parent(trips_by_id[stop_time['trip_id']])
  
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
  def _read_children(self):
    # Are we the only agency in the feed?
    check = lambda r:True
    if len(self._feed.agencies()) > 1:
      check = lambda r:(r.get('agency_id') == self.id())
    # Get the routes...    
    return set(
      filter(check, self._feed.iterread('routes'))
    )
  
  def routes(self):
    """Return all routes for this agency."""
    return set(self.children()) # copy
  
  def route(self, id):
    """Return a single route by ID."""
    return util.filtfirst(self.routes(), id=id)
  
  def trips(self):
    """Return all trips for this agency."""
    trips = set()
    for route in self.routes():
      trips |= route.trips()
    return trips
  
  def trip(self, id):
    """Return a single trip by ID."""
    return util.filtfirst(self.trips(), id=id)

  def stops(self):
    """Return all stops visited by trips for this agency."""
    stops = set()
    for stop_time in self.stop_times():
      stops |= stop_time.stops()
    return stops

  def stop(self, id):
    """Return a single stop by ID."""
    return util.filtfirst(self.stops(), id=id)
    
  def stop_times(self):
    """Return all stop_times for this agency."""
    stop_times = set()
    for trip in self.trips():
      stop_times |= trip.stop_times()
    return stop_times
    
  ##### Validation #####
    
  def validate(self):
    # Required
    assert self.get('agency_name')
    assert self.get('agency_url').startswith('http')
    assert pytz.timezone(self.get('agency_timezone'))
    # Optional
    if self.get('agency_id'):
      pass
    if self.get('agency_phone'):
      pass
    if self.get('agency_lang'):
      assert iso639.get_language(self.get('agency_lang'))
    if self.get('agency_fare_url'):
      assert self.get('agency_fare_url').startswith('http')
