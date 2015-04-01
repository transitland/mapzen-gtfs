"""GTFS Feed Reader."""
import csv
import zipfile
import collections
import json

import unicodecsv

import util
import entities

class Feed(object):
  """Read a GTFS feed."""

  # Classes for each GTFS table.
  factories = {
    'agency': entities.Agency,
    'routes': entities.Route,
    'trips': entities.Trip,
    'stops': entities.Stop,
    'stop_times': entities.StopTime,
    None: entities.Entity
  }

  def __init__(self, filename, debug=False):
    """Filename required."""
    self.cache = {}
    self.filename = filename
    self.zipfile = zipfile.ZipFile(filename)
    self.debug = debug

  def iterread(self, filename):
    """Iteratively read data from a GTFS table. Returns namedtuples."""
    if self.debug:
      print "reading: %s.txt"%filename
    factory = self.factories.get(filename) or self.factories.get(None)
    with self.zipfile.open('%s.txt'%filename) as f:
      data = unicodecsv.reader(f, encoding='utf-8-sig')
      tableheader = data.next()
      tableclass = collections.namedtuple(
        'EntityNamedTuple', 
        map(str, tableheader)
      )
      for row in data:
        yield factory(tableclass._make(row), feed=self)
        
  def read(self, filename):
    """Read all the data from a GTFS table. Returns namedtuples."""
    if filename in self.cache:
      return self.cache[filename]
    try:
      data = list(self.iterread(filename))
    except KeyError:
      data = []
    self.cache[filename] = data
    return data

  def agencies(self):
    """Return the agencies in this feed."""
    return self.read('agency')

  def agency(self, id):
    """Return a single agency by ID."""
    return util.filtfirst(self.agencies(), id=id)

  def routes(self):
    """Return the routes in this feed."""
    return self.read('routes')

  def route(self, id):
    """Return a single route by ID."""
    return util.filtfirst(self.routes(), id=id)

  def stops(self):
    """Return the stops."""
    return self.read('stops')

  def stop(self, id):
    """Return a single stop by ID."""
    return util.filtfirst(self.stop(), id=id)
