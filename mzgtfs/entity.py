"""Base entity."""

from . import validation

class Entity(object):
  """A GTFS Entity.

  Parent-child relationships:

    Agency ->
      Route ->
        Trip ->
          StopTime ->
            Stop

  """
  ENTITY_TYPE = None
  KEY = None
  REQUIRED = []
  OPTIONAL = []

  def __init__(self, **data):
    """Row data from DictReader, and reference to feed."""
    # The row data.
    # This is a collections.namedtuple, and is read-only.
    self.data = data
    # Reference to GTFS Reader.
    self._feed = None
    # Relationships (e.g. trips, stop_times, ...)
    self._children = set()
    self._parents = set()

  def __repr__(self):
    return '<%s %s>'%(self.__class__.__name__, self.id())

  # GTFS row data.
  def __len__(self):
    return len(self.data)

  def __contains__(self, key):
    return key in self.data

  def __getitem__(self, key):
    """Proxy to row data."""
    # Work with either a dict or a namedtuple.
    if hasattr(self.data, '_fields'):
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
    if hasattr(self.data, '_fields'):
      self.data = self.data._asdict()
    self.data[key] = value

  def set_feed(self, feed):
    self._feed = feed

  def keys(self):
    if hasattr(self.data, '_fields'):
      return self.data._fields
    return list(self.data.keys())

  def items(self):
    if hasattr(self.data, '_fields'):
      return list(self.data._asdict().items())
    return list(self.data.items())

  # Name methods.
  def name(self):
    """A reasonable name for the entity."""
    return None

  def id(self):
    """An internal GTFS identifier, e.g. route_id."""
    return None

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
    return self._children

  # ... parents
  def add_parent(self, parent):
    """Add a parent relationship."""
    self.pclink(parent, self)

  def parents(self):
    """Read and cache parents."""
    return self._parents

  def _read_parents(self):
    """Read the parents from the GTFS feed."""
    return set()

  ##### Validation #####

  def validate(self, validator=None):
    return validation.make_validator(validator)

  def validate_feed(self, validator=None):
    return validation.make_validator(validator)
