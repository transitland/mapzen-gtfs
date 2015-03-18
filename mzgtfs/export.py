"""Provide useful information about a GTFS file."""
import argparse
import json

import reader

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='GTFS Information')
  parser.add_argument('filename', help='GTFS File')
  parser.add_argument('--debug', 
    help='Show helpful debugging information', 
    action='store_true')

  args = parser.parse_args()
  g = reader.Reader(args.filename)
  print "===== GTFS: %s ====="%g.filename
  for agency in g.agencies():
    agency.preload()
    print "Agency:", agency['agency_name']
    print "  Routes:", len(agency.routes())
    if args.debug:
      for route in agency.routes():
        print route.data
    print "  Stops:", len(agency.stops())
    if args.debug:
      for stop in agency.stops():
        print stop.data
    print "  Trips:", len(agency.trips())
    if args.debug:
      for trip in agency.trips():
        print trip.data

    # Export
    outfile = 'g-%s.geojson'%agency.id()
    print "Writing: %s"%outfile
    with open(outfile, 'w') as f:
      json.dump(
        agency.geojson(), 
        f, 
        sort_keys=True, 
        indent=4, 
        separators=(',', ': ')
      )
