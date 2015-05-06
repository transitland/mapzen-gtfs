"""Validation exceptions and managers."""
import traceback
import contextlib

def make_validator(validator=None):
  return validator or ValidationManager()

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
    print "===== Validation Errors ====="
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
