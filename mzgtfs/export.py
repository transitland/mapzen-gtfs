"""Provide useful information about a GTFS file and export to JSON."""
import argparse
import json

from . import feed

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='GTFS Info and JSON export')
  parser.add_argument('filename', help='GTFS File')
  parser.add_argument('--debug', 
    help='Show helpful debugging information', 
    action='store_true')

  args = parser.parse_args()
  g = feed.Feed(args.filename)
  g.preload()
  print("===== GTFS: %s ====="%g.filename)
  for agency in g.agencies():
    print("Agency:", agency['agency_name'])
    print("  Routes:", len(agency.routes()))
    if args.debug:
      for route in agency.routes():
        print(route.data)
    print("  Stops:", len(agency.stops()))
    if args.debug:
      for stop in agency.stops():
        print(stop.data)
    print("  Trips:", len(agency.trips()))
    if args.debug:
      for trip in agency.trips():
        print(trip.data)

    # Export
    outfile = 'export-%s.geojson'%agency.id()
    print("Writing: %s"%outfile)
    with open(outfile, 'w') as f:
      json.dump(
        agency.json(), 
        f, 
        sort_keys=True, 
        indent=4, 
        separators=(',', ': ')
      )
