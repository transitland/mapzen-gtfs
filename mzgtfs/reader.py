"""GTFS tools."""
import csv
import zipfile

import unicodecsv

import entities

class Reader(object):
  factories = {
    'agency.txt': entities.Agency,
    'routes.txt': entities.Route,
    'stops.txt': entities.Stop,
    None: entities.Entity
  }

  def __init__(self, filename):
    self.cache = {}
    self.filename = filename
    self.zipfile = zipfile.ZipFile(filename)

  def readcsv(self, filename):
    factory = self.factories.get(filename) or self.factories.get(None)
    with self.zipfile.open(filename) as f:
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
    return self.read('agency.txt')  
    
