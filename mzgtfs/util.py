"""Utilities."""

import os

def filtany(entities, **kw):
  """Filter a set of entities based on method return. Use keyword arguments.
  
  Example:
    filtmeth(entities, id='123')
    filtmeth(entities, name='bart')

  Multiple filters are 'OR'.
  """
  ret = set()
  for k,v in list(kw.items()):
    for entity in entities:
      if getattr(entity, k)() == v:
        ret.add(entity)
  return ret

def filtfirst(entities, **kw):
  """Return the first matching entity, sorted by id()."""
  ret = sorted(filtany(entities, **kw), key=lambda x:x.id())
  if not ret:
    raise ValueError('No result')
  return ret[0]

##### Utilities for tests #####

def example_feed(feed='sample-feed.zip'):
  return os.path.join(
    os.path.dirname(__file__), 
    'examples',
    feed
    )
  
def preload_agency(**kw):
  from . import feed  
  agency_id = kw.pop('agency_id', 'DTA')
  f = feed.Feed(example_feed(**kw))
  f.preload()
  agency = f.agency(agency_id)
  return agency
