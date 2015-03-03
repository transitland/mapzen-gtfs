"""Compare two GTFS feeds."""
import sys
import json
import collections
import argparse
import pprint

import reader

def strip(s):
  return str(s).strip().lower()

def stripvalues(d,keys):
  return tuple(strip(d.get(k)) for k in keys)

class GTFSCompare(object):
  def __init__(self, filename1, filename2):
    self.g1 = reader.Reader(filename1)
    self.g2 = reader.Reader(filename2)

  def group(self, filename, keys):
    d1 = collections.defaultdict(list)
    d2 = collections.defaultdict(list)    
    for i in self.g1.read(filename):
      d1[stripvalues(i,keys)].append(i)
    for i in self.g2.read(filename):
      d2[stripvalues(i,keys)].append(i)
    return d1, d2
    
  def same(self, filename, keys):
    d1, d2 = self.group(filename, keys)
    ret = {}
    for i in set(d1.keys()) & set(d2.keys()):
      ret[i] = d2[i]
    return ret  

  def new(self, filename, keys):
    d1, d2 = self.group(filename, keys)
    ret = {}
    for i in set(d2.keys()) - set(d1.keys()):
      ret[i] = d2[i]
    return ret  

  def lost(self, filename, keys):
    d1, d2 = self.group(filename, keys)
    ret = {}
    for i in set(d1.keys()) - set(d2.keys()):
      ret[i] = d1[i]
    return ret  

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='GTFS Comparison Tool')
  parser.add_argument('filename1', help='GTFS File 1')
  parser.add_argument('filename2', help='GTFS File 2')
  parser.add_argument('--table', help='Comparison table (GTFS filename.txt)', default='routes.txt')
  parser.add_argument('--key', help='Comparison key', action="append", dest='keys')
  parser.add_argument('--display', help='Display key', action="append")
  parser.add_argument('--flip', help='Flip comparison', action='store_true')
  parser.add_argument('--debug', help='Debug', action='store_true')
  args = parser.parse_args()
  args.keys = args.keys or ['route_short_name']
  args.display = args.display or ['route_long_name']
  if args.flip:
    args.filename1, args.filename2 = args.filename2, args.filename1
  # 
  gc = GTFSCompare(args.filename1, args.filename2)

  same = gc.same(args.table, keys=args.keys)
  print "===== Same: %s ====="%(len(same))
  for k,v in sorted(same.items()):
    print k, [stripvalues(i,args.display) for i in v]
    if args.debug:
      pprint.pprint([i.data for i in v])

  lost = gc.lost(args.table, keys=args.keys)
  print "===== Lost: %s ====="%(len(lost))
  for k,v in sorted(lost.items()):
    print k, [stripvalues(i,args.display) for i in v]
    if args.debug:
      pprint.pprint([i.data for i in v])

  new = gc.new(args.table, keys=args.keys)
  print "===== New: %s ====="%(len(new))
  for k,v in sorted(new.items()):
    print k, [stripvalues(i,args.display) for i in v]
    if args.debug:
      pprint.pprint([i.data for i in v])
