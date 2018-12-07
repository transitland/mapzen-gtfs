"""GTFS Frequency."""
import datetime

from . import entity
from . import geom
from . import util
from . import widetime
from . import validation

class Frequency(entity.Entity):
  REQUIRED = [
    'trip_id',
    'start_time',
    'end_time',
    'headway_secs'
  ]
  OPTIONAL = [
    'exact_times'
  ]

  def start(self):
    return widetime.WideTime.from_string(self.get('start_time'))

  def end(self):
    return widetime.WideTime.from_string(self.get('end_time'))

  def validate(self, validator=None):
    validator = super(Frequency, self).validate(validator)
    # Required
    with validator(self):
      assert self.get('trip_id'), "Required: trip_id"
    with validator(self):
      assert self.get('start_time'), "Required: start_time"
    with validator(self):
      assert self.get('end_time'), "Required: end_time"
    with validator(self):
      assert validation.valid_widetime(self.get('start_time')), \
        "Invalid start_time"
    with validator(self):
      assert validation.valid_widetime(self.get('end_time')), \
        "Invalid end_time"
    with validator(self):
      assert self.end() >= self.start(), \
        "Invalid end_time, must at least start_date"
    with validator(self):
      assert validation.valid_int(self.get('headway_secs'), vmin=1), \
        "Invalid headway_secs"
    # Optional
    with validator(self):
      if self.get('exact_times'):
        assert validation.valid_bool(self.get('exact_times'), empty=True), \
          "Invalid exact_times"
    return validator

  def validate_feed(self, validator=None):
    validator = super(Frequency, self).validate_feed(validator)
    with validator(self):
      assert self._feed.trip(self.get('trip_id')), "Unknown trip_id"
    return validator
