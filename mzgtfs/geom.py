"""Geometry utilities."""
from functools import reduce
# Bounding box
def bbox(features):
  points = [s.point() for s in features]
  if not points:
    raise ValueError("Cannot create bbox with no features.")
  lons = [p[0] for p in points]
  lats = [p[1] for p in points]
  return [
    min(lons),
    min(lats),
    max(lons),
    max(lats)
  ]
  
# Convex hull - Graham Scan - Tom Switzer <thomas.switzer@gmail.com>
# http://tomswitzer.net/2010/03/graham-scan/
TURN_LEFT, TURN_RIGHT, TURN_NONE = (1, -1, 0)

def cmp(a,b):
  return (a > b) - (a < b)

def _turn(p, q, r):
    return cmp((q[0] - p[0])*(r[1] - p[1]) - (r[0] - p[0])*(q[1] - p[1]), 0)
 
def _keep_left(hull, r):
    while len(hull) > 1 and _turn(hull[-2], hull[-1], r) != TURN_LEFT:
            hull.pop()
    if not len(hull) or hull[-1] != r:
        hull.append(r)
    return hull
 
def convex_hull(features):
    """Returns points on convex hull of an array of points in CCW order."""
    points = sorted([s.point() for s in features])
    l = reduce(_keep_left, points, [])
    u = reduce(_keep_left, reversed(points), [])
    return l.extend(u[i] for i in range(1, len(u) - 1)) or l

