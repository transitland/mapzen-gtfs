"""Test utilities."""
import unittest
import os
import json
import inspect

import geom

class MockPoint(object):
  def __init__(self, x, y):
    self.x = x
    self.y = y
  def point(self):
    return [self.x,self.y]

def mockpoints():
  return [
    MockPoint(0,1),
    MockPoint(1,0),
    MockPoint(1,1)
  ]

class TestGeom(unittest.TestCase):
  def test_bbox(self):
    expect = [0, 0, 1, 1]
    data = geom.bbox(mockpoints())
    for i,j in zip(data, expect):
      assert i == j
      
  def test_bbox_nopoints(self):
    with self.assertRaises(ValueError):
      geom.bbox([])
      
  def test_convex_hull(self):
    expect = [[0, 1], [1, 0], [1, 1]]
    data = geom.convex_hull(mockpoints())
    for i,j in zip(data, expect):
      self.assertAlmostEqual(i[0], j[0])
      self.assertAlmostEqual(i[1], j[1])
