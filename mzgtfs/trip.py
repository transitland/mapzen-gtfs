"""GTFS Trip entity."""

import entity
import validation

class Trip(entity.Entity):
  """GTFS Trip entity."""
  entity_type = 't'
  
  def id(self):
    return self.get('trip_id')
  
  # Graph
  def _read_children(self):
    """Return stop_times for this trip."""
    return set([
      stop_time for stop_time
      in self._feed.iterread('stop_times')
      if stop_time.get('trip_id') == self.id()
    ])
    
  def stop_times(self):
    return set(self.children()) # copy

  # Trip methods.
  def stop_sequence(self):
    """Return the sorted StopTimes for this trip."""
    return sorted(
      self.stop_times(), 
      key=lambda x:int(x.get('stop_sequence'))
    )
    
  ##### Validation #####
  def validate(self, validator=None):
    validator = validation.make_validator(validator)
    # Required
    with validator(self): 
      assert self.get('route_id'), "Required: route_id"
    with validator(self): 
      assert self.get('service_id'), "Required: service_id"
    with validator(self): 
      assert self.get('trip_id'), "Required: trip_id"
    # Optional
    with validator(self):
      if self.get('direction_id'):
        assert int(self.get('direction_id')) in [0,1], "Invalid direction_id, must be 0,1: %s"%self.get('direction_id')
    with validator(self):
      if self.get('wheelchair_accessible'):
        assert int(self.get('wheelchair_accessible')) in [0,1,2], "Invalid wheelchair_accessible, must be 0,1,2: %s"%self.get('wheelchair_accessible')
    with validator(self):
      if self.get('bikes_allowed'):
        assert int(self.get('bikes_allowed')) in [0,1,2], "Invalid bikes_allowed, must be 0,1,2: %s"%self.get('bikes_allowed')
    with validator(self):
      if self.get('trip_headsign'):
        pass
    with validator(self):
      if self.get('trip_short_name'):
        pass
    with validator(self):
      if self.get('block_id'):
        pass
    with validator(self):
      if self.get('shape_id'):
        pass
