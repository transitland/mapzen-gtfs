"""Entity unit tests."""
import unittest
import os
import json
import collections
import copy

import feed
import entities
import util

class TestEntity(unittest.TestCase):
  """Test Entity methods, and unimplemented abstract methods."""
  expect = collections.OrderedDict({
    'foo':'bar',
    'rab':'oof'
  })

  def test_init(self):
    agency = entities.Entity(**self.expect)
  
  def test_get(self):
    agency = entities.Entity(**self.expect)
    for key in self.expect.keys():
      assert agency.get(key) == self.expect.get(key)
      assert agency[key] == self.expect[key]

  def test_get_keyerror(self):
    agency = entities.Entity(**self.expect)    
    with self.assertRaises(KeyError):
      agency['asdf']
  
  def test_get_default(self):
    agency = entities.Entity(**self.expect)    
    assert agency.get('asdf','test') == 'test'
    
  def test_get_namedtuple(self):
    nt = collections.namedtuple('test', self.expect.keys())
    agency = entities.Entity.from_row(nt(**self.expect))
    for key in self.expect.keys():
      assert agency.get(key) == self.expect.get(key)
      assert agency[key] == self.expect[key]

  def test_get_namedtuple_keyerror(self):
    nt = collections.namedtuple('test', self.expect.keys())
    agency = entities.Entity.from_row(nt(**self.expect))
    with self.assertRaises(KeyError):
      agency['asdf']

  def test_setitem(self):
    agency = entities.Entity(**self.expect)
    agency.set('test', 'ok')
    assert agency['test'] == 'ok'
  
  def test_setitem_ntconvert(self):
    nt = collections.namedtuple('test', self.expect.keys())
    agency = entities.Entity.from_row(nt(**self.expect))
    agency.set('test', 'ok')
    assert agency['test'] == 'ok'    

  def test_name(self):
    entity = entities.Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.name()

  def test_id(self):
    entity = entities.Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.id()

  def test_point(self):
    entity = entities.Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.point()

  def test_bbox(self):
    entity = entities.Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.bbox()

  def test_geometry(self):
    entity = entities.Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.geometry()

  def test_from_json(self):
    with self.assertRaises(NotImplementedError):
      entities.Entity.from_json(self.expect)

  def test_json(self):
    entity = entities.Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.json()

  # Relationships
  def test_pclink(self):
    agency1 = entities.Entity(**self.expect)    
    agency2 = entities.Entity(**self.expect)    
    agency1.pclink(agency1, agency2)
    assert agency2 in agency1.children()
    assert agency1 in agency2.parents()

  def test_add_child(self):
    agency1 = entities.Entity(**self.expect)    
    agency2 = entities.Entity(**self.expect)    
    agency1.add_child(agency2)
    assert agency2 in agency1.children()
    assert agency1 in agency2.parents()

  def test_add_parent(self):
    agency1 = entities.Entity(**self.expect)    
    agency2 = entities.Entity(**self.expect)    
    agency2.add_parent(agency1)
    assert agency2 in agency1.children()
    assert agency1 in agency2.parents()

  def test_parents(self):
    self.test_add_parent()
    entity = entities.Entity(**self.expect)    
    assert not entity.parents()
  
  def test_children(self):
    self.test_add_child()
    entity = entities.Entity(**self.expect)    
    assert not entity.children()
    
    

