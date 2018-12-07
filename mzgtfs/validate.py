"""Validate a GTFS file."""
import argparse
import json

from . import feed
from . import validation

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Validate a GTFS feed.')
  parser.add_argument('filename', help='GTFS File')
  parser.add_argument('--debug', 
    help='Show helpful debugging information', 
    action='store_true')
  args = parser.parse_args()
  
  validator = validation.ValidationReport()
  feed = feed.Feed(args.filename, debug=args.debug)
  feed.validate(validator=validator)
  validator.report()