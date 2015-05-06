"""Validate a GTFS file."""
import argparse
import json

import feed
import validation

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='GTFS Info and JSON export')
  parser.add_argument('filename', help='GTFS File')
  parser.add_argument('--debug', 
    help='Show helpful debugging information', 
    action='store_true')
  args = parser.parse_args()
  
  validator = validation.ValidationReport()
  feed = feed.Feed(args.filename, debug=args.debug)
  feed.validate(validator=validator)
  validator.report()