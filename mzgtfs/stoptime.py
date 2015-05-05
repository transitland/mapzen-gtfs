"""GTFS StopTime entity."""
import entity

class StopTime(entity.Entity):
  """GTFS Stop Time Entity."""
  
  def point(self):
    # Ugly hack.
    return list(self._children)[0].point()

  # Graph
  def stops(self):
    return set(self.children())