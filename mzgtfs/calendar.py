"""GTFS Calendar entity."""
import datetime

import entity
import geom
import util
import validation

class Calendar(entity.Entity):
  def start(self):
    return datetime.datetime.strptime(self.get('start_date'), '%Y%M%d')

  def end(self):
    return datetime.datetime.strptime(self.get('end_date'), '%Y%M%d')

  def validate(self, validator=None):
    validator = validation.make_validator(validator)
