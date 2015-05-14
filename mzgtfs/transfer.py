"""GTFS Transfers."""
import datetime

import entity
import geom
import util
import widetime
import validation

class Transfer(entity.Entity):
  REQUIRED = [
    'from_stop_id',
    'to_stop_id',
    'transfer_type'
  ]
  OPTIONAL = [
    'min_transfer_time'
  ]
  
  def validate(self, validator=None):
    validator = super(Transfer, self).validate(validator)
    # Required
    with validator(self):
      assert self.get('from_stop_id'), "Required: from_stop_id"
    with validator(self):
      assert self.get('to_stop_id'), "Required: to_stop_id"
    with validator(self):
      # field required, blank allowed.
      assert validation.valid_int(self.get('transfer_type'), vmin=0, vmax=3), \
        "Invalid transfer_type"
    with validator(self):
      if self.get('min_transfer_time'):
        assert validation.valid_int(self.get('min_transfer_time'), vmin=0), \
        "Invalid min_transfer_time"
    return validator
    
  def validate_feed(self, validator=None):
    validator = super(FareRule, self).validate_feed(validator)
    with validator(self):
      assert self._feed.stop(self.get('from_stop_id')), "Unknown from_stop_id"
    with validator(self):
      assert self._feed.stop(self.get('to_stop_id')), "Unknown to_stop_id"
    return validator