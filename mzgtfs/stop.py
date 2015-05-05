"""GTFS Stop entity."""
import entity

class Stop(entity.Entity):  
  """GTFS Stop entity."""
  entity_type = 's'

  def id(self):
    return self.get('stop_id')

  def name(self):
    return self.get('stop_name')
    
  def point(self):
    try:
      return float(self.get('stop_lon')), float(self.get('stop_lat'))
    except ValueError, e:
      print "Warning: no stop_lon, stop_lat:", self.name(), self.id()
      return None

  def bbox(self):
    c = self.point()
    return [c[0], c[1], c[0], c[1]]

  def json(self):
    return {
      'type': 'Feature',
      'name': self.name(),
      'properties': self.data,
      'bbox': self.bbox(),
      'geometry': self.geometry()
    }
  
  def geometry(self):
    return {
      "type": 'Point',
      "coordinates": self.point(),
    }

  # Stop methods.
  def routes(self):
    serves = set()
    for stop_time in self._parents:
      for trip in stop_time._parents:
        serves |= trip._parents
    return serves
