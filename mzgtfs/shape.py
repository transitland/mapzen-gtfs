"""GTFS ShapeRow entity; these can be collected into a ShapeLine"""
import entity
import validation

class ShapeLine(entity.Entity):
  """A collection of ShapeRows."""
  def rows(self):
    return sorted(
      self._children, 
      key=lambda x:int(x.get('shape_pt_sequence',0))
    )

  def points(self):
    return [i.point() for i in self.rows()]

  def geometry(self):
    return {
      'type':'MultiLineString',
      'coordinates': [self.points()]
    }
  
  def json(self):
    return {
      'type': 'Feature',
      'properties': self.data,
      'geometry': self.geometry()
    }
      
class ShapeRow(entity.Entity):
  """A row in shapes.txt"""
  REQUIRED = [
    'shape_id',
    'shape_pt_lat',
    'shape_pt_lon',
    'shape_pt_sequence',
    
  ]
  OPTIONAL = [
    'shape_dist_traveled',
  ]
  
  def id(self):
    return self.get('shape_id')

  def name(self):
    return self.get('shape_id')  
  
  def point(self):
    try:
      return float(self.get('shape_pt_lon')), float(self.get('shape_pt_lat'))
    except ValueError, e:
      print "Warning: no shape_pt_lon, shape_pt_lat:", self.name(), self.id()
      return None

  def geometry(self):
    return {
      "type": 'Point',
      "coordinates": self.point(),
    }

  def validate(self, validator=None):
    validator = super(ShapeRow, self).validate(validator)
    # Required
    with validator(self):
      assert validation.valid_int(self.get('shape_pt_sequence'), vmin=0), \
        "Required: shape_pt_sequence"
    with validator(self): 
      assert self.get('shape_pt_lat'), "Required: shape_pt_lat"
    with validator(self): 
      assert self.get('shape_pt_lon'), "Required: shape_pt_lon"
    with validator(self): 
      assert validation.valid_point(self.point()), \
      "Invalid shape_pt_lon or shape_pt_lat"
    # Optional
    return validator
