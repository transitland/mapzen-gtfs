"""GTFS Trip entity."""
import entity
import validation

class Trip(entity.Entity):
  """GTFS Trip entity."""
  ENTITY_TYPE = 't'
  KEY = 'trip_id'
  REQUIRED = [
    'trip_id',
    'route_id',
    'service_id',
  ]
  OPTIONAL = [
    'trip_headsign',
    'trip_short_name',
    'direction_id',
    'block_id',
    'shape_id',
    'wheelchair_accessible',
    'bikes_allowed',
  ]
  def id(self):
    return self.get('trip_id')

  def start(self):
    return self.stop_sequence()[0].arrive()

  def end(self):
    return self.stop_sequence()[-1].arrive()

  # Graph
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
    validator = super(Trip, self).validate(validator)
    # Required
    with validator(self):
      assert self.get('route_id'), "Required: route_id"
    with validator(self):
      assert self.get('service_id'), "Required: service_id"
    with validator(self):
      assert self.get('trip_id'), "Required: trip_id"
    # TODO: Warnings:
    #   speed/vehicle_type
    #   duplicate trips
    # Optional
    with validator(self):
      if self.get('direction_id'):
        assert validation.valid_bool(self.get('direction_id')), "Invalid direction_id"
    with validator(self):
      if self.get('wheelchair_accessible'):
        assert validation.valid_int(self.get('wheelchair_accessible'), vmin=0, vmax=2, empty=True), \
          "Invalid wheelchair_accessible"
    with validator(self):
      if self.get('bikes_allowed'):
        assert validation.valid_int(self.get('bikes_allowed'), vmin=0, vmax=2, empty=True), \
          "Invalid bikes_allowed"
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

  def validate_feed(self, validator=None):
    validator = super(Trip, self).validate_feed(validator)
    with validator(self):
      assert self._feed.route(self.get('route_id')), "Unknown route_id"
    with validator(self):
      assert self._feed.service_period(self.get('service_id')), "Unknown service_id"
    with validator(self):
      cur = 0
      for i in self.stop_sequence():
        j = int(i.get('stop_sequence'))
        assert j > cur, \
          "Invalid stop_time sequence: stop_sequence must increase"
        cur = j
    # TODO: validate shape
    return validator
