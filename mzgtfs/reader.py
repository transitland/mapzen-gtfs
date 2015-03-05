"""GTFS tools."""
import csv
import zipfile

import json
import unicodecsv

import entities

class Reader(object):
  factories = {
    'agency': entities.Agency,
    'routes': entities.Route,
    'stops': entities.Stop,
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
    self.zipfile = zipfile.ZipFile(filename)

  def open_geojson(self, filename):
    with open(filename) as f:
      data = json.load(f)
    agency = entities.Agency.from_geojson(data)
    self.cache['agency'] = [agency]
    self.cache['stops'] = agency.cache['stops']
    self.cache['routes'] = []

  def readcsv(self, filename):
    factory = self.factories.get(filename) or self.factories.get(None)
    with self.zipfile.open('%s.txt'%filename) as f:
      data = unicodecsv.DictReader(f, encoding='utf-8-sig')
      for i in data:
        yield factory(i, feed=self)
    return
        
  def read(self, filename):
    if filename in self.cache:
      return self.cache[filename]
    try:
      data = list(self.readcsv(filename))
    except KeyError:
      data = []
    self.cache[filename] = data
    return data

  def agencies(self):
    return self.read('agency')  
    
  def stops(self):
    return self.read('stops')
    
