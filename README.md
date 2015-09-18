# Mapzen GTFS

[![Circle CI](https://circleci.com/gh/transitland/mapzen-gtfs.png?style=badge)](https://circleci.com/gh/transitland/mapzen-gtfs)

A simple GTFS library.

Benefits:

 * Fast parser
 * Reads directly from zip archives
 * Entity generators, read tables line-by-line
 * Entity graph structure
 * Reads directly from zip archives
 * Built-in basic validator

## Installation

Installation using pip:

```
pip install mzgtfs
```

Alternatively, [download from PyPi](https://pypi.python.org/pypi/mzgtfs) or clone this repository, and install using setup.py:

```
python ./setup.py install
```

The dependency [unicodecsv](https://pypi.python.org/pypi/unicodecsv) will be automatically installed using the above methods.

## Supported GTFS Entities

The GTFS CSV files are mapped to the following Entity classes:

| File                | Class                | Feed access methods
|---------------------|----------------------|-----------------|
| agency.txt          | Agency               | agencies(), agency(agency_id)
| routes.txt          | Route                | routes(), route(route_id)
| trips.txt           | Trip                 | trips(), trip(trip_id)
| stops.txt           | Stop                 | stops(), stop(stop_id)
| stop_times.txt      | StopTime             | stop_times()
| shapes.txt          | ShapeLine            | shape_line(shape_id)
| calendar.txt        | ServicePeriod        | service_periods(), service_period(service_id)
| calendar_dates.txt  | ServiceDate          | service_exceptions()
| fare_attributes.txt | FareAttribute        | fares(), fare(fare_id)
| fare_rules.txt      | FareRule             | fare_rules()
| transfers.txt       | Transfer             | transfers()
| frequencies.txt     | Frequency            | frequencies()
| feed_info.txt       | FeedInfo             | feed_infos()

## Reading tables

The main Feed class `mzgtfs.feed.Feed` supports loading data from a feed using the methods above. It accepts either the filename of a GTFS zip file, or a path to a directory of CSV files.

```
>>> import mzgtfs.feed
>>> gtfs_feed = mzgtfs.feed.Feed(filename='current.zip') # alt., path=<dir>
>>> gtfs_feed.routes()
[<Route BFC>, <Route CITY>, <Route STBA>, <Route AB>, <Route AAMV>]
>>> gtfs_feed.route('BFC')
<Route BFC>
>>> gtfs_feed.route('BFC').name()
u'Demo route'
```

## Entity generator

Each of the access methods in the above table will read the CSV file and cache the resulting entities. If you want to read a table line-by-line with lower overhead, you can use `iterread(table)`. This is especially useful with stop_times.txt, which may have millions of rows.

```
>>> for route in gtfs_feed.iterread('routes'): print route
<Route AB>
<Route BFC>
<Route STBA>
<Route CITY>
<Route AAMV>
```

## Working with an Agency

Many GTFS contain multiple agencies. You can construct a graph for each agency that includes only the relevant routes, stops, etc., by calling preload(). This can then be searched, or exported using json(). `Agency` provides a subset of the above access methods, including `stops(), stop(stop_id), routes(), route(route_id), trips(), and trip(trip_id)`

```
>>> gtfs_feed.preload() # Load all tables and create relationships
>>> gtfs_feed.agencies()
[<Agency DTA>, <Agency ATD>]
>>> dta = gtfs_feed.agency('DTA')
>>> len(dta.routes())
5
>>> len(dta.stops())
9
>>> dta.routes()
set([<Route STBA>, <Route CITY>, <Route AB>, <Route AAMV>, <Route BFC>])
>>> dta.route('CITY').name()
u'40'
>>> dta.json()
{'name': u'Demo Transit Authority', ..... }
```

## Validating a Feed

This library contains a basic GTFS validator. It validates required and optional attributes and their values, foreign keys, and requirements such as stop sequences.

Additionally, a wrapper to Google's Transitfeed `feedvalidator.py` is provided, if it is available on your system. This provides additional checks, as well as warnings for common feed problems such as date ranges, stop spacing, bus speeds, etc. However, this is currently only supported on zip'd feeds; if you have made any changes, you will have to write out a zip file first.

```
>>> import mzgtfs.feed
>>> import mzgtfs.validation
>>> validator = mzgtfs.validation.ValidationReport()
>>> feed = mzgtfs.feed.Feed('current.zip')
>>> feed.validate(validator=validator)
>>> feed.validate_feedvalidator(validator=validator)
>>> validator.report()
Validation report:
<Feed .//mzgtfs/examples/sample-feed.zip>: Errors reported by feedvalidator.py; see report.html for details
```

## Writing

## Contributing

Please [open a Github issue](https://github.com/transitland/mapzen-gtfs/issues/new) with as much of the following information as you're able to specify, or [contact us](#contact) for assistance.

## Contact

Transitland is sponsored by [Mapzen](http://mapzen.com). Contact us with your questions, comments, or suggests: [hello@mapzen.com](mailto:hello@mapzen.com).
