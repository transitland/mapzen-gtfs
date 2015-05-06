"""GTFS StopTime entity."""

import entity
import validation

class WideTime(object):
  def __init__(self, hours=0, minutes=0, seconds=0):
    assert 0 <= hours
    assert 0 <= minutes <= 60
    assert 0 <= seconds <= 60
    self.hours = hours
    self.minutes = minutes
    self.seconds = seconds
  
  @classmethod
  def from_string(cls, value):
    return cls(*map(int, value.split(':')))

  def __str__(self):
    return ':'.join('%02d'%i for i in list(self))

  def __iter__(self):
    return iter([self.hours, self.minutes, self.seconds])

  def __lt__(self, other):
    return list(self) < list(other)

  def __le__(self, other):
    return list(self) <= list(other)
  
  def __gt__(self, other):
    return list(self) > list(other)
  
  def __ge__(self, other):
    return list(self) >= list(other)
    
  def __eq__(self, other):
    return list(self) == list(other)

class StopTime(entity.Entity):
  """GTFS Stop Time Entity."""
  
  def point(self):
    # Ugly hack.
    return list(self._children)[0].point()

  # Graph
  def stops(self):
    return set(self.children())
    
  def arrive(self):
    if self.get('arrival_time'):
      return WideTime.from_string(self.get('arrival_time'))
    
  def depart(self):
    if self.get('departure_time'):
      return WideTime.from_string(self.get('departure_time'))
    
  def sequence(self):
    return int(self.get('stop_sequence'))  
    
  ##### Validation #####
  def validate(self, validator=None):
    validator = validation.make_validator(validator)
    # Required
    with validator(self): 
      assert self.get('stop_id'), "Required: stop_id"
    with validator(self): 
      assert self.get('trip_id'), "Required: trip_id"
    with validator(self): 
      assert self.get('stop_sequence'), "Required: stop_sequence"
    with validator(self):
      if self.get('arrival_time'):
        assert WideTime.from_string(self.get('arrival_time')), "Invalid arrival_time: %s"%self.get('arrival_time')
    with validator(self):
      if self.get('departure_time'):
        assert WideTime.from_string(self.get('departure_time')), "Invalid departure_time: %s"%self.get('departure_time')
    with validator(self): 
      assert self.arrive() <= self.depart(), "Cannot depart before arriving!: %s -> %s"%(self.arrive(), self.depart())
    with validator(self):
      assert self.sequence() >= 0, "Invalid stop_sequence: %s"%self.get('stop_sequence')
    # Optional
    with validator(self):
      if self.get('pickup_type'):
        assert int(self.get('pickup_type')) in [0,1,2,3], "Invalid pickup_type, must be 0,1,2,3: %s"%self.get('pickup_type')
    with validator(self): 
      if self.get('drop_off_type'):
        assert int(self.get('drop_off_type')) in [0,1,2,3], "Invalid drop_off_type, must be 0,1,2,3: %s"%self.get('drop_off_type')
    with validator(self):
      if self.get('timepoint'):
        assert int(self.get('timepoint')) in [0,1], "Invalid timepoint, must be 0,1: %s"%self.get('timepoint')
    with validator(self):
      if int(self.get('timepoint',0)) == 1:
        assert self.arrive() and self.depart(), "Exact timepoints require arrival_time and departure_time"
    with validator(self):
      if self.get('stop_headsign'):
        pass
    with validator(self):
      if self.get('shape_dist_traveled'):
        pass
