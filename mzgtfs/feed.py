"""GTFS Feed Reader."""
import csv
import zipfile
import collections
import json
import os
import tempfile
import glob

import csv
try:
  import unicodecsv
except ImportError:
  unicodecsv = None

import util
import entities
import validation
  
class Feed(object):
  """Read a GTFS feed."""

  # Classes for each GTFS table.
  FACTORIES = {
    'agency': entities.Agency,
    'routes': entities.Route,
    'trips': entities.Trip,
    'stops': entities.Stop,
    'stop_times': entities.StopTime,
    'shapes': entities.ShapeRow,
    'calendar': entities.ServicePeriod,
    'fare_rules': entities.FareRule,
    'fare_attributes': entities.FareAttribute,
    'transfers': entities.Transfer,
    'frequencies': entities.Frequency,
    'feed_info': entities.FeedInfo
  }

  def __init__(self, filename=None, path=None, debug=False):
    """Filename required."""
    self.cache = {}
    self.by_id = {}
    self.filename = filename
    self.path = path
    self.debug = debug

  ##### Read / write #####

  def _open(self, table):
    arcname = '%s.txt'%table
    f = None
    zf = None
    if self.path and os.path.exists(os.path.join(self.path, arcname)):
      f = open(os.path.join(self.path, arcname))
    elif self.filename and os.path.exists(self.filename):
      zf = zipfile.ZipFile(self.filename)
      try:
        f = zf.open(arcname)
      except KeyError:
        pass
    if not f:
      raise KeyError("File not found in path or zip file: %s"%arcname)
    return f

  def iterread(self, table):
    """Iteratively read data from a GTFS table. Returns namedtuples."""
    if self.debug: # pragma: no cover
      print "Reading:", table
    # Entity class
    cls = self.FACTORIES[table]
    f = self._open(table)
    # csv reader
    if unicodecsv:
      data = unicodecsv.reader(f, encoding='utf-8-sig')
    else:
      data = csv.reader(f)
    header = data.next()
    headerlen = len(header)
    ent = collections.namedtuple(
      'EntityNamedTuple', 
      map(str, header)
    )
    for row in data:
      if len(row) == 0:
        continue
      # Get rid of extra spaces.
      row = [i.strip() for i in row]
      # pad to length if necessary... :(
      if len(row) < headerlen:
        row += ['']*(headerlen-len(row))
      yield cls.from_row(ent._make(row), self)
    f.close()
    
  def read(self, table):
    """..."""
    # Table exists
    if table in self.by_id:
      return self.by_id[table].values()
    if table in self.cache:
      return self.cache[table]    
    # Read table
    cls = self.FACTORIES[table]
    key = cls.KEY
    if key:
      if table not in self.by_id:
        self.by_id[table] = {}
      t = self.by_id[table]
      for item in self.iterread(table):
        t[item.get(key)] = item
      return t.items()
    if table not in self.cache:
      self.cache[table] = []
    t = self.cache[table]
    for item in self.iterread(table):
      t.append(item)
    return t

  def write(self, filename, entities, sortkey=None, columns=None):
    """Write entities out to filename in csv format.
    
    Note: this doesn't write directly into a Zip archive, because this behavior
    is difficult to achieve with Zip archives. Use make_zip() to create a new
    GTFS Zip archive.
    """    
    if os.path.exists(filename):
      raise IOError('File exists: %s'%filename)
    # Make sure we have all the entities loaded.
    if sortkey:
      entities = sorted(entities, key=lambda x:x[sortkey])
    if not columns:
      columns = set()
      for entity in entities:
        columns |= set(entity.keys())
      columns = sorted(columns)      
    # Write the csv file
    with open(filename, 'wb') as f:
      writer = unicodecsv.writer(f) # , encoding='utf-8-sig'
      writer.writerow(columns)
      for entity in entities:
        writer.writerow([entity.get(column) for column in columns])

  def make_zip(self, filename, path=None, files=None, clone=None):
    """Create a Zip archive.
    
    Provide any of the following:
      path - A directory of .txt files
      files - A list of files
      clone - Copy any files from a zip archive not specified above
     """
    if filename and os.path.exists(filename):
      raise IOError('File exists: %s'%filename)     
    files = set(files or [])
    if path and os.path.isdir(path):
      files |= set(glob.glob(os.path.join(path, '*.txt')))
    # Check unique
    arcnames = set([os.path.basename(f) for f in files])
    common = arcnames & files
    if common:
      raise ValueError("Files must be unique: %s"%", ".join(common))
    # Write files.
    if self.debug: # pragma: no cover
      print "Creating zip archive:", filename
    zf = zipfile.ZipFile(filename, 'a')
    # Clone from existing zip archive.
    if clone and os.path.exists(clone):
      zc = zipfile.ZipFile(clone, 'a')
      # Filter out external files.  
      for i in [j for j in zc.namelist() if j not in arcnames]:
        if self.debug: # pragma: no cover
          print "... copying:", i
        with zc.open(i) as f:
          data = f.read()
        zf.writestr(i, data)
    for f in files:
      if self.debug: # pragma: no cover
        print "... adding:", f
      zf.write(f, os.path.basename(f))
    zf.close()

  def preload(self):
    # Load tables with primary key
    for table,cls in self.FACTORIES.items():
      if not cls.KEY:
        continue
      try:
        self.read(table)
      except KeyError:
        pass
    for route in self.routes():
      route.add_parent(self.agency(route.get('agency_id')))
    for trip in self.trips():
      trip.add_parent(self.route(trip.get('route_id')))
    # Load stop_times  
    for stoptime in self.read('stop_times'):
      stoptime.add_parent(self.trip(stoptime.get('trip_id')))
      stoptime.add_child(self.stop(stoptime.get('stop_id')))

  ##### Keyed entities #####
  
  def agencies(self):
    """Return the agencies in this feed."""
    return self.read('agency')

  def agency(self, key):
    """Return a single agency by ID."""
    if 'agency' not in self.by_id:
      self.read('agency')
    return self.by_id['agency'][key]

  def routes(self):
    """Return the routes in this feed."""
    return self.read('routes')

  def route(self, key):
    """Return a single route by ID."""
    if 'routes' not in self.by_id:
      self.read('routes')
    return self.by_id['routes'][key]

  def stops(self):
    """Return the stops."""
    return self.read('stops')

  def stop(self, key):
    """Return a single stop by ID."""
    if 'stops' not in self.by_id:
      self.read('stops')
    return self.by_id['stops'][key]
  
  def trips(self):
    """Return the trips."""
    return self.read('trips')

  def trip(self, key):
    """Return a single trip by ID."""
    if 'trips' not in self.by_id:
      self.read('trips')
    return self.by_id['trips'][key]
  
  def shapes(self):
    """Return the route shapes as a dictionary."""
    # Todo: Cache?
    # Group together by shape_id
    if self.debug: # pragma: no cover
      print "Generating shapes..."
    ret = collections.defaultdict(entities.ShapeLine)
    for point in self.read('shapes'):
      ret[point['shape_id']].add_child(point)
    return ret
    
  ##### Other methods #####
  
  def dates(self):
    data = self.read('calendar')
    return [
      min(i.start() for i in data),
      max(i.end() for i in data)
    ]
    
  ##### Validation #####
  
  def validate(self, validator=None):
    validator = validation.make_validator(validator)
    print "Building feed graph..."
    self.preload()
    print "...Done"
    # required
    required = [
      'agency', 
      'stops', 
      'routes', 
      'trips',
      'stop_times',
      'calendar'
    ]
    for f in required:
      print "Validating required file:", f
      data = self.read(f)
      for i in data:
        i.validate(validator=validator)    
    # optional
    optional = [
      'calendar_dates',
      'fare_attributes',
      'fare_rules',
      'shapes',
      'frequencies',
      'transfers',
      'feed_info'
    ]
    for f in optional:
      print "Validating optional file:", f
      try:
        data = self.read(f)
      except KeyError, e:
        data = []
      for i in data:
        i.validate(validator=validator)
    return validator

