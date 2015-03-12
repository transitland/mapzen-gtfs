"""GTFS tools."""
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

  def __init__(self, filename):
    self.cache = {}
    self.filename = filename
    self.zipfile = None
    if filename.endswith('.zip'):
      self.open_zip(filename)
    elif filename.endswith('.geojson'):
      self.open_geojson(filename)

  def open_zip(self, filename):
    """Open a GTFS zip file."""
    self.zipfile = zipfile.ZipFile(filename)

  def open_geojson(self, filename):
    """Open and read a GeoJSON representation of the GTFS feed."""
    with open(filename) as f:
      data = json.load(f)
    agency = entities.Agency.from_geojson(data)
    self.cache['agency'] = [agency]
    self.cache['stops'] = agency.cache['stops']
    self.cache['routes'] = []
    
  def readiter(self, filename, **kw):
    """Iteratively read data from a zipped csv file."""
    print "reading: %s.txt"%filename
    factory = self.factories.get(filename) or self.factories.get(None)
    with self.zipfile.open('%s.txt'%filename) as f:
      data = unicodecsv.DictReader(f, encoding='utf-8-sig')
      for row in data:
        yield factory(row, feed=self, **kw)
        
  def read(self, filename):
    """Read all the data from a zipped csv file."""
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
