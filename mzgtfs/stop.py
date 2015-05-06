"""GTFS Stop entity."""
import entity
import validation

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
  def validate(self, validator=None):
    validator = validation.make_validator(validator)
    # Required
    with validator(self): 
      assert self.get('stop_id'), "Required: stop_id"
    with validator(self): 
      assert self.get('stop_name'), "Required: stop_name"
    with validator(self): 
      assert self.get('stop_lat'), "Required: stop_lat"
    with validator(self): 
      assert self.get('stop_lon'), "Required: stop_lon"
    with validator(self): 
      assert self.point(), "Unable to create point from (stop_lon,stop_lat)"
    with validator(self): 
      assert -180 <= self.point()[0] <= 180, "Longitude out of bounds: %s"%self.point()[0]
    with validator(self): 
      assert -90 <= self.point()[1] <= 90, "Latitude out of bounds: %s"%Self.point()[1]
    # Optional
    with validator(self):
      if self.get('stop_desc') == self.get('stop_name'):
        raise validation.ValidationWarning("stop_desc and stop_name are the same")        
    with validator(self):
      if self.get('zone_id') and int(self.get('location_type') or 0):
        raise validation.ValidationWarning("zone_id set on a station")
    with validator(self): 
      if self.get('stop_url'):
        assert self.get('stop_url').startswith('http'), "stop_url must begin with http(s):// scheme"
    with validator(self): 
      if self.get('location_type'):
        assert int(self.get('location_type') or 0) in [0,1], "Invalid location_type, must be 0, 1: %s"%self.get('location_type')
    with validator(self):
      if int(self.get('location_type') or 0) and self.get('parent_station'):
        assert not self.get('parent_station'), "A station cannot contain another station"          
    with validator(self): 
      if self.get('stop_timezone'):
        assert pytz.timezone(self.get('stop_timezone')), "Invalid timezone: %s"%self.get('stop_timezone')
    with validator(self): 
      if self.get('wheelchair_boarding'):
        assert int(self.get('wheelchair_boarding') or 0) in [0,1,2], "Invalid wheelchair_boarding, must be 0, 1, 2: %s"%self.get('wheelchair_boarding')
    with validator(self):
      if self.get('stop_code'):
        pass
