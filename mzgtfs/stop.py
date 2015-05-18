"""GTFS Stop entity."""
import entity
import validation

class Stop(entity.Entity):  
  """GTFS Stop entity."""
  ENTITY_TYPE = 's'
  KEY = 'stop_id'
  REQUIRED = [
    'stop_id',
    'stop_name',
    'stop_lat',
    'stop_lon'     
  ]
  OPTIONAL = [
    'stop_code',
    'stop_desc',
    'zone_id',
    'stop_url',
    'location_type',
    'parent_station',
    'stop_timezone',
    'wheelchair_boarding'
  ]
  
  def id(self):
    return self.get('stop_id')

  def name(self):
    return self.get('stop_name')
    
  def point(self):
    try:
      return float(self.get('stop_lon')), float(self.get('stop_lat'))
    except ValueError, e:
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
    validator = super(Stop, self).validate(validator)
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
      assert validation.valid_point(self.point()), "Invalid stop_lon/stop_lat"
    # TODO: Warnings: 
    #  - stop too close to 0,0
    # Optional
    with validator(self):
      if self.get('stop_desc') == self.get('stop_name'):
        raise validation.ValidationWarning("stop_desc and stop_name are the same")        
    with validator(self):
      if self.get('zone_id') and int(self.get('location_type') or 0):
        raise validation.ValidationWarning("A station cannot have a zone_id")
    with validator(self): 
      if self.get('stop_url'):
        assert validation.valid_url(self.get('stop_url')), "Invalid stop_url"
    with validator(self): 
      if self.get('location_type'):
        assert validation.valid_bool(self.get('location_type'), empty=True), \
          "Invalid location_type"
    with validator(self):
      if int(self.get('location_type') or 0) and self.get('parent_station'):
        assert not self.get('parent_station'), \
          "A station cannot contain another station"          
    with validator(self):
      if self.get('stop_timezone'):
        assert validation.valid_tz(self.get('stop_timezone')), "Invalid timezone"
    with validator(self): 
      if self.get('wheelchair_boarding'):
        assert validation.valid_int(self.get('wheelchair_boarding'), vmin=0, vmax=2, empty=True), \
          "Invalid wheelchair_boarding"
    with validator(self):
      if self.get('stop_code'):
        pass
    return validator
    
  def validate_feed(self, validator=None):
    validator = super(Stop, self).validate_feed(validator)  
    with validator(self):
      if self.get('parent_station'):
        parent_station = self._feed.stop(self.get('parent_station'))
        assert parent_station, "Unknown parent_station"
        assert int(parent_station.get('location_type') or 0) == 1, \
          "Invalid parent_station, parent must have location_type set to 1."
    return validator
    