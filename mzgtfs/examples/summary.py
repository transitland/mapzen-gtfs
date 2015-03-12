import sys
import os
import json
import glob

import mzgtfs.reader

def aggregate(filenames, outfile):
  features = []
  for filename in filenames:
    for g in glob.glob(os.path.join(os.path.dirname(filename), '*.geojson')):
      print g
      with open(g) as f:
        data = json.load(f)
      b = data.bbox()
      features.append({
        'type':'Feature',
        'properties': data['properties'],
        'geometry': {
          'type': 'Polygon',
          'coordinates': [[
            [b[0], b[1]],
            [b[0], b[3]],
            [b[2], b[3]],
            [b[2], b[1]],
            [b[0], b[1]]
          ]]}
        })
    out = {
      'type':'FeatureCollection',
      'features': features
    }
    with open(outfile, 'w') as f:
      json.dump(out, f)

def summarize(filename):
  d = os.path.dirname(filename)
  # Create OnestopIds for each agency.
  g = mzgtfs.reader.Reader(filename)
  for agency in g.agencies():
    print "Agency:", agency.get('agency_name')
    try:
      o = agency.onestop()
      print "Got Onestop ID:", o
    except Exception, e:
      print "Error on agency:", e
      continue
    
    if not agency.stops():
      print "No stops! Skipping"
      continue

    # Write geojson agency data.
    data = agency.geojson()
    with open(os.path.join(d, '%s.geojson'%o), 'w') as f:
      f.write(json.dumps(data))
      
if __name__ == "__main__":
  for filename in sys.argv[1:]:
    print "==== %s ===="%filename
    summarize(filename)
  # aggregate(sys.argv[1:], 'coverage.geojson')
  
  