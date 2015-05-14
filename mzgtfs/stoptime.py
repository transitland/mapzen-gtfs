"""GTFS StopTime entity."""
import entity
import widetime
import validation

class StopTime(entity.Entity):
  """GTFS Stop Time Entity."""
  REQUIRED = [
    'trip_id',
    'arrival_time',
    'departure_time',
    'stop_id',
    'stop_sequence',    
  ]
  OPTIONAL = [
    'stop_headsign',
    'pickup_type',
    'drop_off_type',
    'shape_dist_traveled',
    'timepoint'
  ]
  
  def point(self):
    # Ugly hack.
    return list(self._children)[0].point()

  def arrive(self):
    if self.get('arrival_time'):
      return widetime.WideTime.from_string(self.get('arrival_time'))
    
  def depart(self):
    if self.get('departure_time'):
      return widetime.WideTime.from_string(self.get('departure_time'))
    
  def sequence(self):
    return int(self.get('stop_sequence'))  
    
  # Graph
  def stops(self):
    return set(self.children())

  ##### Validation #####
  def validate(self, validator=None):
    validator = super(StopTime, self).validate(validator)
    # Required
    with validator(self):
      assert self.get('trip_id'), "Required: trip_id"
    with validator(self):
      assert \
        (self.get('arrival_time') and self.get('departure_time')) or \
        (not self.get('arrival_time') and not self.get('departure_time')), \
        "Both arrival_time and departure_time must be set, or both must be empty."
    with validator(self):
      if self.get('arrival_time'):
        assert validation.valid_widetime(self.get('arrival_time')), \
          "Invalid arrival_time: %s"%self.get('arrival_time')
    with validator(self):
      if self.get('departure_time'):
        assert validation.valid_widetime(self.get('departure_time')), \
          "Invalid departure_time: %s"%self.get('departure_time')
    with validator(self): 
      assert self.arrive() <= self.depart(), \
        "Cannot depart before arriving!: %s -> %s"%(self.arrive(), self.depart())
    with validator(self):
      assert self.sequence() >= 0, \
        "Invalid stop_sequence: %s"%self.get('stop_sequence')
    # TODO: Warnings - useless stops (cant pickup or dropoff)
    # Optional
    with validator(self):
      if self.get('pickup_type'):
        assert validation.valid_int(self.get('pickup_type'), vmin=0, vmax=3), \
          "Invalid pickup_type, must be 0,1,2,3: %s"%self.get('pickup_type')
    with validator(self): 
      if self.get('drop_off_type'):
        assert validation.valid_int(self.get('drop_off_type'), vmin=0, vmax=3), \
          "Invalid drop_off_type, must be 0,1,2,3: %s"%self.get('drop_off_type')
    with validator(self):
      if self.get('timepoint'):
        assert validation.valid_bool(self.get('timepoint')), \
          "Invalid timepoint"
    with validator(self):
      if int(self.get('timepoint',0)) == 1:
        assert self.arrive() and self.depart(), \
          "Exact timepoints require arrival_time and departure_time"
    with validator(self):
      if self.get('stop_headsign'):
        pass
    with validator(self):
      if self.get('shape_dist_traveled'):
        pass
    return validator
