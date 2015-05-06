"""GTFS Trip entity."""
import entity

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
  def validate(self):
    # Required
    assert self.get('route_id')
    assert self.get('service_id')
    assert self.get('trip_id')
    # Optional
    if self.get('trip_headsign'):
      pass
    if self.get('trip_short_name'):
      pass
    if self.get('direction_id'):
      assert int(self.get('direction_id')) in [0,1]
    if self.get('block_id'):
      pass
    if self.get('shape_id'):
      pass
    if self.get('wheelchair_accessible'):
      assert int(self.get('wheelchair_accessible')) in [0,1,2]
    if self.get('bikes_allowed'):
      assert int(self.get('bikes_allowed')) in [0,1,2]
