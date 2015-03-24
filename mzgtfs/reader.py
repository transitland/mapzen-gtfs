"""GTFS Feed Reader."""
import csv
import zipfile
import collections
import json

import unicodecsv

import entities

class Reader(object):
  """Read a GTFS feed."""

  # Classes for each zipped file.
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

  def readiter(self, filename, **kw):
    """Iteratively read data from a GTFS table."""
    if self.debug:
      print "reading: %s.txt"%filename
    factory = self.factories.get(filename) or self.factories.get(None)
    with self.zipfile.open('%s.txt'%filename) as f:
      data = unicodecsv.DictReader(f, encoding='utf-8-sig')
      for row in data:
        yield factory(row, feed=self, **kw)
        
  def read(self, filename):
    """Read all the data from a GTFS table."""
    if filename in self.cache:
      return self.cache[filename]
    try:
      data = list(self.readiter(filename))
    except KeyError:
      data = []
    self.cache[filename] = data
    return data

  def agencies(self):
    """Return the agencies in this feed."""
    return self.read('agency')
