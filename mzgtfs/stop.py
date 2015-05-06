"""GTFS Stop entity."""
import entity

class Stop(entity.Entity):  
  """GTFS Stop entity."""
  entity_type = 's'

  def id(self):
    return self.get('stop_id')

  def name(self):
    return self.get('stop_name')
    
  def point(self):
    try:
      return float(self.get('stop_lon')), float(self.get('stop_lat'))
    except ValueError, e:
      print "Warning: no stop_lon, stop_lat:", self.name(), self.id()
      return None

  def bbox(self):
    c = self.point()
    return [c[0], c[1], c[0], c[1]]

  def json(self):
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

  # Stop methods.
  def routes(self):
    serves = set()
    for stop_time in self._parents:
      for trip in stop_time._parents:
        serves |= trip._parents
    return serves

  ##### Validation #####
  def validate(self):
    # Required
    assert self.get('stop_id')
    assert self.get('stop_name')
    assert self.get('stop_lat')
    assert self.get('stop_lon')
    assert self.point() # check as float
    assert -180 <= self.point()[0] <= 180
    assert -90 <= self.point()[1] <= 90 
    # Optional
    if self.get('stop_code'):
      pass
    if self.get('stop_desc'):
      # TODO: if stop_desc = stop_name, warn.
      pass
    if self.get('zone_id'):
      # TODO: If zone_id and station, warn.
      pass
    if self.get('stop_url'):
      assert self.get('stop_url').startswith('http')
    if self.get('location_type'):
      assert int(self.get('location_type')) in [0,1]
    if self.get('parent_station'):
      assert not self.get('zone_id')
      assert self.get('location_type') != '1'
    if self.get('stop_timezone'):
      assert pytz.timezone(self.get('stop_timezone'))
    if self.get('wheelchair_boarding'):
      assert int(self.get('wheelchair_boarding')) in [0,1,2]
      
