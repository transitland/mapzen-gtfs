"""Provide useful information about a GTFS file."""
import argparse
import json

import reader

def jp(data, key):
  return ", ".join(sorted(set(i.get(key).strip() for i in data)))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='GTFS Information')
  parser.add_argument('filename', help='GTFS File')
  parser.add_argument('--debug', 
    help='Show helpful debugging information', 
    action='store_true')
  parser.add_argument('--geojson', 
    help='Write GeoJSON representation to file')

  args = parser.parse_args()
  g = reader.Reader(args.filename)
  print "===== GTFS: %s ====="%g.filename
  for agency in g.agencies():
    agency.preload()
    print "Agency:", agency['agency_name']
    print "  Onestop ID:", agency.onestop()
    print "  Routes:", len(agency.routes())
    print "  Stops:", len(agency.stops())
    if args.debug:
      for stop in agency.stops():
        print stop.onestop()
    print "  Trips:", len(agency.trips())

    if args.geojson:
      with open(args.geojson, 'w') as f:
        json.dump(agency.geojson(), f)

