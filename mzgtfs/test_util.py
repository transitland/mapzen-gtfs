"""Test utilities."""
import unittest
import os
import json
import inspect

from . import util
from . import feed
from . import entities

class TestUtil(unittest.TestCase):
  testdata = [
    entities.Agency(agency_name='Foo', agency_id='1'),
    entities.Agency(agency_name='Bar', agency_id='2'),
    entities.Agency(agency_name='Baz', agency_id='2'),
  ]

  def test_filtany_name(self):
    data = util.filtany(self.testdata, name='Foo')
    assert len(data) == 1
    data = util.filtany(self.testdata, name='Bar')
    assert len(data) == 1
    data = util.filtany(self.testdata, name='Baz')
    assert len(data) == 1

  def test_filtany_id(self):
    data = util.filtany(self.testdata, id='1')
    assert len(data) == 1
    data = util.filtany(self.testdata, id='2')
    assert len(data) == 2
    
  def test_filtfirst_name(self):
    data = util.filtfirst(self.testdata, name='Foo')
    assert data.name() == 'Foo'

  def test_filtfirst_id(self):
    data = util.filtfirst(self.testdata, id='1')
    assert data.id() == '1'
  
  def test_filtfirst_empty(self):
    with self.assertRaises(ValueError):
      util.filtfirst(self.testdata, name='Asdf')
    with self.assertRaises(ValueError):
      util.filtfirst(self.testdata, id='0')
      
  def test_example_feed(self):
    expect = util.example_feed()
    assert os.path.exists(expect)
