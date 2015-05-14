"""WideTime, a time class that supports long days."""
import time

class WideTime(object):
  def __init__(self, hours=0, minutes=0, seconds=0):
    assert 0 <= hours
    assert 0 <= minutes <= 60
    assert 0 <= seconds <= 60
    self.hours = hours
    self.minutes = minutes
    self.seconds = seconds
  
  def as_seconds(self):
    return self.hours * 3600 + self.minutes * 60 + self.seconds
    
  def __add__(self, other):
    return self.as_seconds() + other.as_seconds()
  
  def __sub__(self, other):
    return self.as_seconds() - other.as_seconds()
  
  @classmethod
  def from_string(cls, value):
    return cls(*map(int, value.split(':')))

  def __str__(self):
    return ':'.join('%02d'%i for i in list(self))

  def __iter__(self):
    return iter([self.hours, self.minutes, self.seconds])

  def __lt__(self, other):
    return list(self) < list(other)

  def __le__(self, other):
    return list(self) <= list(other)
  
  def __gt__(self, other):
    return list(self) > list(other)
  
  def __ge__(self, other):
    return list(self) >= list(other)
    
  def __eq__(self, other):
    return list(self) == list(other)