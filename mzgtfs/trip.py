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