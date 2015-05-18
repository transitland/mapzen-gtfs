"""Validation exceptions and managers."""
import pytz
import traceback
import contextlib
import datetime

import iso639
import widetime

def make_validator(validator=None):
  return validator or ValidationManager()

def valid_color(color):
  color = str(color).lower().strip()
  if len(color) != 6:
    return False
  for j in [color[i:i+2] for i in range(0,5,2)]:
    try:
      j = int(j,16)
    except ValueError, e:
      return False
  return True
  
def valid_url(url):
  return url.startswith('http')

def valid_tz(tz):
  return pytz.timezone(tz)

def valid_language(lang):
  return iso639.get_language(lang)

def valid_int(value, vmin=None, vmax=None, empty=False):
  # Allow empty string if empty=True
  if value == '' and empty:
    return True
  try:
    value = int(value)
  except ValueError, e:
    return False
  if vmin is not None and value < vmin:
    return False    
  if vmax is not None and value > vmax:
    return False
  return True
  
def valid_float(value, vmin=None, vmax=None, empty=False):
  # Allow empty string if empty=True
  if value == '' and empty:
    return True
  try:
    value = float(value)
  except ValueError, e:
    return False
  if vmin is not None and value < vmin:
    return False    
  if vmax is not None and value > vmax:
    return False
  return True

def valid_in(value, within):
  return value in within

def valid_bool(value, empty=False):
  if value == '' and empty:
    return True
  try:
    value = int(value)
  except ValueError, e:
    return False
  return value in [0,1]

def valid_date(value, empty=False):
  if not value and empty:
    return True
  if len(value) != 8:
    return False
  try:
    datetime.datetime.strptime(value, '%Y%m%d')
  except ValueError, e:
    return False
  return True

def valid_widetime(value):
  if len(value.split(':')) != 3:
    return False
  if len(value) < 7:
    return False
  if len(value) > 8:
    return False
  try:
    widetime.WideTime.from_string(value)
  except ValueError:
    return False
  return True

def valid_point(point):
  if len(point) != 2:
    return False  
  lon, lat = point
  if not (-180 <= lon <= 180):
    return False
  if not (-90 <= lat <= 90):
    return False
  return True

##### Validation Exceptions #####

class ValidationException(Exception):
  def __init__(self, message, source=None):
    super(ValidationException, self).__init__(message)
    self.source = source

class ValidationError(ValidationException):
  """Base validation error."""
  pass

class ValidationWarning(ValidationException):
  """Validation warning."""
  pass
  
class ValidationInfo(ValidationException):
  """Validation info."""
  pass

##### Validation Managers #####

class ValidationManager(object):
  def __init__(self):
    # List of exceptions generated
    self.exceptions = []
    # Source of ValidationError
    self.source = None 
  
  def __call__(self, source=None):
    self.source = source
    return self
  
  def __enter__(self):
    return self
  
  def __exit__(self, etype, value, traceback):
    self.source = None
    return
      
  def report(self):
    print "Validation report:"
    for e in self.exceptions:
      print "%s: %s"%(e.source, e.message)

class ValidationReport(ValidationManager):
  def __exit__(self, etype, value, traceback):
    # Unset the source from this context.
    s = self.source
    self.source = None
    if not etype:
      return
    if issubclass(etype, AssertionError):
      etype = ValidationError
    if issubclass(etype, ValidationException):
      self.exceptions.append(etype(value, source=s))
      return True

