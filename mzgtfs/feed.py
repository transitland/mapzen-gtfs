"""GTFS Feed Reader."""
import csv
import zipfile
import collections
import json
import os
import tempfile
import glob
import subprocess
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
    'calendar_dates': entities.ServiceDate,
    'fare_rules': entities.FareRule,
    'fare_attributes': entities.FareAttribute,
    'transfers': entities.Transfer,
    'frequencies': entities.Frequency,
    'feed_info': entities.FeedInfo
  }

  def __init__(self, filename=None, path=None, debug=False):
    """Filename required."""
    self.filename = filename
    self.path = path
    self.debug = debug
    self.cache = {}
    self.by_id = {}
    self._shapes = None
    self._zones = None

  ##### Read / write #####
  
  def log(self, msg):
    if self.debug:
      print msg

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
    elif self.filename and not os.path.exists(self.filename):
      raise KeyError("File not found: %s"%self.filename)
    if not f:
      raise KeyError("File not found in path or zip file: %s"%arcname)
    return f

  def iterread(self, table):
    """Iteratively read data from a GTFS table. Returns namedtuples."""
    self.log('Reading: %s'%table)
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
      return t.values()
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

  def make_zip(self, filename, files=None, path=None, clone=None):
    """Create a Zip archive.
    
    Provide any of the following:
      files - A list of files
      path - A directory of .txt files
      clone - Copy any files from a zip archive not specified above

    Duplicate files will be ignored. The 'files' argument will be used first,
    then files found in the specified 'path', then in the 
    specified 'clone' archive.
    """
    if filename and os.path.exists(filename):
      raise IOError('File exists: %s'%filename)     
    files = files or []
    arcnames = []
    if path and os.path.isdir(path):
      files += glob.glob(os.path.join(path, '*.txt'))
    # Write files.
    self.log("Creating zip archive: %s"%filename)
    zf = zipfile.ZipFile(filename, 'a')
    for f in files:
      base = os.path.basename(f)
      if base in arcnames:
        self.log('... skipping: %s'%f)
      else:
        self.log('... adding: %s'%f)
        arcnames.append(base)
        zf.write(f, base)

    # Clone from existing zip archive.
    if clone and os.path.exists(clone):
      zc = zipfile.ZipFile(clone)
      for f in zc.namelist():
        base = os.path.basename(f)
        if os.path.splitext(base)[-1] != '.txt':
          pass
          # self.log('... skipping from clone: %s'%f)
        elif base in arcnames:
          self.log('... skipping from clone: %s'%f)
        else:
          self.log('... adding from clone: %s'%f)
          arcnames.append(base)
          with zc.open(f) as i:
            data = i.read()
          zf.writestr(base, data)
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

    default_agency_id = None
    agencies = self.agencies()
    if len(agencies) == 1:
      default_agency_id = agencies[0].get('agency_id')

    for route in self.routes():
      route.add_parent(self.agency(route.get('agency_id') or default_agency_id))
    for trip in self.trips():
      trip.add_parent(self.route(trip.get('route_id')))
    # Load stop_times  
    for stoptime in self.read('stop_times'):
      stoptime.add_parent(self.trip(stoptime.get('trip_id')))
      stoptime.add_child(self.stop(stoptime.get('stop_id')))

  ##### Keyed entities #####
  
  def _entities(self, table):
    return self.read(table)
  
  def _entity(self, table, key):
    if table not in self.by_id:
      self.read(table)
    return self.by_id[table][key]
    
  def agencies(self): return self._entities('agency')
  def agency(self, key): return self._entity('agency', key)
  def routes(self): return self._entities('routes')
  def route(self, key): return self._entity('routes', key)
  def stops(self): return self._entities('stops')
  def stop(self, key): return self._entity('stops', key)
  def trips(self): return self._entities('trips')
  def trip(self, key): return self._entity('trips', key)
  def fares(self): return self._entities('fare_attributes')
  def fare(self, key): return self._entity('fare_attributes', key)
  def serviceperiods(self): return self._entities('calendar')
  def serviceperiod(self, key): return self._entity('calendar', key)

  def shapes(self):
    """Return the route shapes as a dictionary."""
    # Todo: Cache?
    if self._shapes:
      return self._shapes
    # Group together by shape_id
    self.log("Generating shapes...")
    ret = collections.defaultdict(entities.ShapeLine)
    for point in self.read('shapes'):
      ret[point['shape_id']].add_child(point)
    self._shapes = ret
    return self._shapes
    
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
    self.log('Loading...')
    self.preload()
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
      self.log("Validating required file: %s"%f)
      data = self.read(f)
      for i in data:
        i.validate(validator=validator)
        i.validate_feed(validator=validator)  
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
      self.log("Validating optional file: %s"%f)
      try:
        data = self.read(f)
      except KeyError, e:
        data = []
      for i in data:
        i.validate(validator=validator)
        i.validate_feed(validator=validator)  
    return validator

  def validate_feedvalidator(self, validator=None, report='report.html'):
    validator = validation.make_validator(validator)
    p = subprocess.Popen(
      [
        'feedvalidator.py',
        '--memory_db',
        '--noprompt',
        '--output',
        report,
        self.filename
      ],
      stdout=subprocess.PIPE, 
      stderr=subprocess.PIPE
    )
    stdout, stderr = p.communicate()
    returncode = p.returncode
    with validator(self):
      errors = [i for i in stdout.split('\n') if i.startswith('ERROR:')]
      if returncode:
        raise validation.ValidationError('Errors reported by feedvalidator.py; see %s for details'%report)
