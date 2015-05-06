"""GTFS Calendar entity."""
import datetime

import entity
import geom
import util

class Calendar(entity.Entity):
  def start(self):
    return datetime.datetime.strptime(self.get('start_date'), '%Y%M%d')

  def end(self):
    return datetime.datetime.strptime(self.get('end_date'), '%Y%M%d')
