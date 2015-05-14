"""GTFS entities.

These are now split into separate modules; this module
maintains backwards compatibility.

Classes:
  Entity - GTFS entity base class
  Agency
  Route
  Trip
  StopTime
  Stop

"""
from entity import Entity
from agency import Agency
from route import Route
from trip import Trip
from stop import Stop
from stoptime import StopTime
from shape import ShapeRow, ShapeLine
from serviceperiod import ServicePeriod
from farerule import FareRule
from transfer import Transfer
from frequency import Frequency

# from fareattribute import FareAttribute
FareAttribute = Entity
FeedInfo = Entity