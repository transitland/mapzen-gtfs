"""Base entity."""

class Entity(object):
  """A GTFS Entity.
  
  Parent-child relationships:
  
    Agency -> 
      Route -> 
        Trip -> 
          StopTime -> 
            Stop
  
  """
  entity_type = None

  def __init__(self, **data):
    """Row data from DictReader, and reference to feed."""
    # The row data. 
    # This is a collections.namedtuple, and is read-only.
    self.data = data
    # Reference to GTFS Reader.
    self._feed = None
    # Relationships (e.g. trips, stop_times, ...)
    self._children = None  
    self._parents = None
  
  # GTFS row data.
  def __len__(self):
    return len(self.data)
  
  def __contains__(self, key):
    return key in self.data
  
  def __getitem__(self, key):
    """Proxy to row data."""
    # Work with either a dict or a namedtuple.
    if hasattr(self.data, '_asdict'):
      try:
        return getattr(self.data, key)
      except AttributeError:
        raise KeyError
    else:
      return self.data[key]

  def get(self, key, default=None):
    """Get row data by key."""
    try:
      return self[key]
    except KeyError:
      return default
      
  def set(self, key, value):
    # Convert from namedtuple to dict if setting value.
    if hasattr(self.data, '_asdict'):
      self.data = self.data._asdict()
    self.data[key] = value
  
  def set_feed(self, feed):
    self._feed = feed
  
  def keys(self):
    return self.data.keys()
    
  def items(self):
    return self.data.items()
  
  # Name methods.
  def name(self):
    """A reasonable name for the entity."""
    raise NotImplementedError
  
  def id(self):
    """An internal GTFS identifier, e.g. route_id."""
    raise NotImplementedError
  
  def feedid(self, feedid):
    """A canonical Onestop-style ID for this entity."""
    return 'gtfs://%s/%s/%s'%(
      feedid,
      self.entity_type,
      self.id()
    )

  # Entity geometry.
  def point(self):
    """Return a point for this entity."""
    raise NotImplementedError  
    
  def bbox(self):
    """Return a bounding box for this entity."""
    raise NotImplementedError
  
  def geometry(self):
    """Return a GeoJSON-type geometry for this entity."""
    raise NotImplementedError
    
  # Load / Dump.
  @classmethod
  def from_row(cls, data, feed=None):
    entity = cls()
    entity.data = data
    entity.set_feed(feed)
    return entity
    
  @classmethod
  def from_json(cls, data):
    raise NotImplementedError
  
  def json(self):
    raise NotImplementedError

  # Graph.
  def pclink(self, parent, child):
    """Create a parent-child relationship."""
    if parent._children is None:
      parent._children = set()
    if child._parents is None:
      child._parents = set()
    parent._children.add(child)
    child._parents.add(parent)
    
  # ... children
  def add_child(self, child):
    """Add a child relationship."""
    self.pclink(self, child)
    
  def children(self):
    """Read and cache children."""
    if self._children is not None:
      return self._children
    self._children = self._read_children()
    return self._children
    
  def _read_children(self):
    """Read children from GTFS feed."""
    return set()
  
  # ... parents
  def add_parent(self, parent):
    """Add a parent relationship."""
    self.pclink(parent, self)
    
  def parents(self):
    """Read and cache parents."""
    if self._parents is not None:
      return self._parents
    self._parents = self._read_parents()
    return self._parents
    
  def _read_parents(self):
    """Read the parents from the GTFS feed."""
    return set()
    
  ##### Validation #####
  
  def validate(self):
    return True  
    