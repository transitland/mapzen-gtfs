"""GTFS Fare Attributes."""
import datetime

from . import entity
from . import geom
from . import util
from . import widetime
from . import validation

class FareAttribute(entity.Entity):
  KEY = 'fare_id'
  REQUIRED = [
    'fare_id',
    'price',
    'currency_type',
    'payment_method',
    'transfers',
  ]
  OPTIONAL = [
    'transfer_duration'
  ]
  
  def validate(self, validator=None):
    validator = super(FareAttribute, self).validate(validator)
    # Required
    with validator(self):
      assert self.get('fare_id'), "Required: fare_id"
    with validator(self):
      assert self.get('price'), "Required: price"
    with validator(self):
      assert validation.valid_float(self.get('price')), "Invalid price"
    with validator(self):
      assert self.get('currency_type'), "Required: currency_type"
    with validator(self):
      assert self.get('payment_method'), "Required: payment_method"
    with validator(self):
      assert validation.valid_bool(self.get('payment_method')), \
        "Invalid payment_method"
    with validator(self):
      assert validation.valid_int(self.get('transfers'), vmin=0, vmax=2, empty=True), \
        "Invalid transfers"
    # Optional
    with validator(self):
      if self.get('transfer_duration'):
        assert validation.valid_int(self.get('transfer_duration'), vmin=0), \
          "Invalid transfer_duration"
    return validator
    
  def validate_feed(self, validator=None):
    validator = super(FareAttribute, self).validate_feed(validator)
    return validator