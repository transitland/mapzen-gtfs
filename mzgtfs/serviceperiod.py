"""GTFS ServicePeriod entity."""
import datetime

import entity
import geom
import util
import validation

class ServicePeriod(entity.Entity):
  KEY = 'service_id'
  REQUIRED = [
    'service_id',
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
    'start_date',
    'end_date'
  ]
  OPTIONAL = [
  ]

  def start(self):
    return datetime.datetime.strptime(self.get('start_date'), '%Y%m%d')

  def end(self):
    return datetime.datetime.strptime(self.get('end_date'), '%Y%m%d')

  def validate(self, validator=None):
    validator = super(ServicePeriod, self).validate(validator)
    with validator(self):
      assert self.get('service_id'), "Required: service_id"
    with validator(self):
      assert validation.valid_bool(self.get('monday')), "Required: monday"
    with validator(self):
      assert validation.valid_bool(self.get('tuesday')), "Required: tuesday"
    with validator(self):
      assert validation.valid_bool(self.get('wednesday')), "Required: wednesday"
    with validator(self):
      assert validation.valid_bool(self.get('thursday')), "Required: thursday"
    with validator(self):
      assert validation.valid_bool(self.get('friday')), "Required: friday"
    with validator(self):
      assert validation.valid_bool(self.get('saturday')), "Required: saturday"
    with validator(self):
      assert validation.valid_bool(self.get('sunday')), "Required: sunday"
    with validator(self):
      assert validation.valid_date(self.get('start_date'), empty=True), "Invalid start_date"
    with validator(self):
      assert validation.valid_date(self.get('start_end'), empty=True), "Invalid start_end"
    with validator(self):
      assert self.end() > self.start(), \
        "Invalid end_date, must be greater than start_date"
    # TODO: Warnings
    #   - no days of the week
    return validator
  
class ServiceDate(entity.Entity):
  REQUIRED = [
    'service_id',
    'date',
    'exception_type'
  ]
  
  def validate(self, validator=None):
    validator = super(ServiceDate, self).validate(validator)
    with validator(self):
      assert self.get('service_id'), "Required: service_id"
    with validator(self):
      assert self.get('date'), "Required: date"
    with validator(self):
      assert validation.valid_int(self.get('exception_type'), vmin=1, vmax=2), \
        "Invalid exception_type"
    return validator
    
  def validate_feed(self, validator=None):
    validator = super(ServiceDate, self).validate_feed(validator)
    with validator(self):
      assert self._feed.serviceperiod(self.get('service_id')), \
        "Unknown service_id"    
    return validator