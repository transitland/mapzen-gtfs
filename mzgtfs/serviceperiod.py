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
    return datetime.datetime.strptime(self.get('start_date'), '%Y%M%d')

  def end(self):
    return datetime.datetime.strptime(self.get('end_date'), '%Y%M%d')

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
      assert self.start(), "Invalid start_date"
    with validator(self):
      assert self.end(), "Invalid end_date"
    with validator(self):
      assert self.end() > self.start(), \
        "Invalid end_date, must be greater than start_date"
    # TODO: Warnings
    #   - no days of the week
    return validator
    