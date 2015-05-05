"""Feed unit tests."""
import unittest
import os
import json
import inspect
import tempfile
import csv
import zipfile

import util
import feed
import entities

def test_outfile():
  # Create a temporary filename.
  # You'll have to unlink file when done.
  # This of course is not secure against file creation problems.
  outfile = tempfile.NamedTemporaryFile()
  name = outfile.name
  outfile.close()
  return name

class TestFeed(unittest.TestCase):
  """Test Feed Reader.
  
  TODO: Test Unicode?
  
  """  
  agency_expect = {
    'agency_url': 'http://google.com', 
    'agency_name': 'Demo Transit Authority', 
    'agency_id': 'DTA', 
    'agency_timezone': 'America/Los_Angeles'
  }
  
  route_expect = {
    'route_long_name': 'Airport - Bullfrog', 
    'route_id': 'AB', 
    'route_type': '3', 
    'route_text_color': '', 
    'agency_id': 'DTA', 
    'route_color': '', 
    'route_url': '', 
    'route_desc': '', 
    'route_short_name': '10'
  }
  
  stop_expect = {
    'stop_lat': '36.425288', 
    'stop_lon': '-117.133162', 
    'stop_id': 'FUR_CREEK_RES', 
    'stop_name': 'Furnace Creek Resort (Demo)'
  }

  def test_init(self):
    f = feed.Feed(util.example_feed())
  
  def test_read(self):
    # Test basic read
    f = feed.Feed(util.example_feed())
    data = f.read('stops')
    # check we got 9 entities
    assert len(data) == 9
    # check cache
    assert 'stops' in f.cache
  
  def test_read_path(self):
    # Test overlay
    f = feed.Feed(
      util.example_feed(), 
      path=os.path.dirname(util.example_feed())
    )
    assert f.stop('TEST')
    with self.assertRaises(Exception):
      f.stop('FUR_CREEK_RES')
  
  def test_read_missing(self):
    f = feed.Feed(
      util.example_feed(), 
      path=os.path.dirname(util.example_feed())
    )
    with self.assertRaises(Exception):
      f.read('missing')
  
  def test_iterread(self):
    # Test generator read
    f = feed.Feed(util.example_feed())
    data = f.iterread('stops')
    assert inspect.isgenerator(data)
    assert len(list(data)) == 9

  def test_write(self):
    f = feed.Feed()
    data = [entities.Agency(**self.agency_expect)]
    outfile = test_outfile()
    f.write(outfile, data, sortkey='agency_id')
    # Check the output...
    with open(outfile) as csvfile:
      reader = csv.reader(csvfile)
      headers = reader.next()
      assert len(self.agency_expect.keys()) == len(headers)
      for i in headers:
        assert i in self.agency_expect
      rows = []
      for i in reader:
        rows.append(i)
      assert len(rows) == 1
      row = rows[0]
      for k,v in zip(headers, row):
        assert self.agency_expect[k] == v
    # Delete temp file
    os.unlink(outfile)

  def test_write_exists(self):
    f = feed.Feed()
    data = [entities.Agency(**self.agency_expect)]
    outfile = test_outfile()
    f.write(outfile, data, sortkey='agency_id')
    with self.assertRaises(IOError):
      f.write(outfile, data, sortkey='agency_id')
    os.unlink(outfile)

  def test_make_zip(self):
    f = feed.Feed()
    outfile = test_outfile()
    f.make_zip(
      outfile,
      path=os.path.dirname(util.example_feed()),
      clone=util.example_feed()
    )
    expect = [
      'agency.txt', 
      'calendar.txt', 
      'calendar_dates.txt', 
      'fare_attributes.txt', 
      'fare_rules.txt', 
      'frequencies.txt', 
      'routes.txt', 
      'shapes.txt', 
      'stop_times.txt', 
      'trips.txt', 
      'stops.txt'
    ]
    zf = zipfile.ZipFile(outfile)
    for i,j in zip(sorted(zf.namelist()), sorted(expect)):
      assert i == j
    zf.close()
    os.unlink(outfile)

  def test_make_zip_exists(self):
    f = feed.Feed()
    outfile = test_outfile()
    f.make_zip(
      outfile,
      path=os.path.dirname(util.example_feed()),
      clone=util.example_feed()
    )
    with self.assertRaises(IOError):
      f.make_zip(
        outfile,
        path=os.path.dirname(util.example_feed()),
        clone=util.example_feed()
      )
    os.unlink(outfile)
    
  def test_make_zip_multiplefiles(self):
    f = feed.Feed()
    outfile = test_outfile()
    with self.assertRaises(ValueError):
      f.make_zip(
        outfile,
        files=['stops.txt'],
        path=os.path.dirname(util.example_feed()),
        clone=util.example_feed()
      )

  def test_cache(self):
    f = feed.Feed(util.example_feed())
    # Read a first time
    data1 = f.read('stops')
    # Read a second time
    data2 = f.read('stops')
    assert len(data1) == len(data2)
    assert 'stops' in f.cache
    assert len(data1) == len(f.cache['stops'])

  def test_read_invalidfile(self):
    f = feed.Feed(util.example_feed())
    with self.assertRaises(KeyError):
      f.read('invalidfile')
      
  def test_read_padding(self):
    # The Google GTFS example feed is missing columns in
    # stop_times.txt. Check the padding mechanism works.
    f = feed.Feed(util.example_feed())
    data = f.read('stop_times')
    # Check that all 9 elements are present.
    for entity in f.read('stop_times'):
      assert len(entity) == 9

  def test_agencies(self):
    f = feed.Feed(util.example_feed())
    data = f.agencies()
    assert len(data) == 1
    
  def test_agency(self):
    f = feed.Feed(util.example_feed())
    data = f.agency(self.agency_expect['agency_id'])
    for k in self.agency_expect:
      assert self.agency_expect[k] == data[k]
  
  def test_routes(self):
    f = feed.Feed(util.example_feed())
    assert len(f.routes()) == 5
    
  def test_route(self):
    f = feed.Feed(util.example_feed())
    data = f.route(self.route_expect['route_id'])
    for k in self.route_expect:
      assert self.route_expect[k] == data[k]

  def test_stops(self):
    f = feed.Feed(util.example_feed())
    assert len(f.stops()) == 9

  def test_stop(self):
    f = feed.Feed(util.example_feed())
    data = f.stop(self.stop_expect['stop_id'])
    for k in self.stop_expect:
      assert self.stop_expect[k] == data[k]
