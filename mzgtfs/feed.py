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

class Feed(object):
  """Read a GTFS feed."""

  # Classes for each GTFS table.
  factories = {
    'agency': entities.Agency,
    'routes': entities.Route,
    'trips': entities.Trip,
    'stops': entities.Stop,
    'stop_times': entities.StopTime,
    'shapes': entities.ShapeRow,
    None: entities.Entity
  }

  def __init__(self, filename=None, path=None, debug=False):
    """Filename required."""
    self.cache = {}
    self.filename = filename
    self.path = path
    self.debug = debug

  def iterread(self, table):
    """Iteratively read data from a GTFS table. Returns namedtuples."""
    if self.debug: # pragma: no cover
      print "reading: %s.txt"%table
    # Entity class
    cls = self.factories.get(table) or self.factories.get(None)
    # Archive name
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
        # raise KeyError below
        pass
    if not f:
      raise KeyError("File not found in path or zip file: %s"%arcname)
    # Can't use context manager, since file can come from multiple sources.
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
      # pad to length if necessary... :(
      if len(row) < headerlen:
        row += ['']*(headerlen-len(row))
      yield cls.from_row(ent._make(row), self)
    # Close
    f.close()
    if zf:
      zf.close()
        
  def read(self, table):
    """Read all the data from a GTFS table. Returns namedtuples."""
    if table in self.cache:
      return self.cache[table]
    data = list(self.iterread(table))
    self.cache[table] = data
    return data

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
    return util.filtfirst(self.stops(), id=id)
  
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
    