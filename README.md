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

## Opening a GTFS Feed

The `mzgtfs.feed.Feed` class is the main entry point for reading and writing schedule data. A feed can be read from either a GTFS zip file, or a directory of CSV files. The validation and write methods are discussed later in this document.

| Feed method | Description |
|-------------|-------------|
| init(filename=None, path=None) | Open a feed, given a GTFS zip file or directory
| preload() | Load the entire feed and entity relationships
| read(table) | Return a list of entities from a table; e.g. `feed.read('stops')`
| iterread(table) | Entity generator
| write(filename, entities, sortkey=None, columns=None) | Write a CSV file
| make_zip(filename, files=None, path=None, clone=None) | Create a GTFS zip archive                  
| validate() | Validate feed
| validate_feedvalidator() | Validate using external feedvalidator.py

The GTFS CSV files are mapped to the following Entity classes:

| Feed method                   | GTFS Table          | Entity Class
|-------------------------------|---------------------|-----------------|
| agencies(), agency(agency_id) | agency.txt          | Agency
| routes(), route(route_id)     | routes.txt          | Route
| trips(), trip(trip_id)        | trips.txt           | Trip
| stops(), stop(stop_id)        | stops.txt           | Stop
| stop_times()                  | stop_times.txt      | StopTime
| shape_line(shape_id)          | shapes.txt          | ShapeLine
| service_periods(), service_period(service_id) | calendar.txt | ServicePeriod
| service_exceptions()          | calendar_dates.txt  | ServiceDate
| fares(), fare(fare_id)        | fare_attributes.txt | FareAttribute
| fare_rules()                  | fare_rules.txt      | FareRule
| transfers()                   | transfers.txt       | Transfer
| frequencies()                 | frequencies.txt     | Frequency
| feed_infos()                  | feed_info.txt       | FeedInfo

```
>>> import mzgtfs.feed
>>> gtfs_feed = mzgtfs.feed.Feed(filename='current.zip') # alt., path=<dir>
>>> gtfs_feed.routes()
[<Route BFC>, <Route CITY>, <Route STBA>, <Route AB>, <Route AAMV>]
>>> gtfs_feed.stops()
[<Stop NANAA>, <Stop BULLFROG>, <Stop FUR_CREEK_RES>, <Stop BEATTY_AIRPORT>, <Stop EMSI>, <Stop DADAN>, <Stop NADAV>, <Stop STAGECOACH>, <Stop AMV>]
>>> gtfs_feed.stop('NANAA').json()
{'name': u'North Ave / N A Ave', ... }
```

## GTFS Graph

Feeds are built on relations between entities; for instance, each agency has a number of routes, these routes have trips, and so on. A convenient way to work with a feed is the `preload()` method, which loads the entire feed and constructs a graph of entities. This provides quick access, such as finding all of the routes and stops associated with an agency.

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
>>> dta.route('CITY').stops()
set([<Stop EMSI>, <Stop DADAN>, <Stop NANAA>, <Stop NADAV>, <Stop STAGECOACH>])
```

## Entity generator

Each of the access methods in the above table will read the CSV file and cache the resulting entities. If you want to read a table line-by-line with lower overhead, you can use `iterread(table)`. This is especially useful with stop_times.txt, which may have millions of rows.

```
>>> gtfs_feed.iterread('routes')
<generator object iterread at 0x101cd86e0>
>>> for route in gtfs_feed.iterread('routes'): print route
<Route AB>
<Route BFC>
<Route STBA>
<Route CITY>
<Route AAMV>
```

## Entity methods

The base Entity class provides the following methods.

| Entity method | Description |
|---------------|-------------|
| get(key, default=None) | Get a GTFS attribute
| entity[key] | Get a GTFS attribute
| len(entity) | Number of attributes
| key in entity | Attribute exists in entity
| keys() | List attributes
| items() | Attribute keys, values
| set(key, value) | Set an attribute
| id() | GTFS entity ID, e.g. agency_id, stop_id, etc.
| name() | A reasonable entity name or description
| point() | A point geometry, if one exists
| bbox() | Entity bounding box
| geometry() | A GeoJSON geometry
| children() | Entity children (e.g. agency -> routes)
| add_child(child) | Add a child entity
| parents() | Entity parents (e.g. route -> agencies)
| add_parent(parent) | Add a parent entity
| validate() | Validate entity; you may pass in a reported
| validate_feed() | Validate entity relationships
| json() | JSON representation
| Entity.from_json(data, feed) | Class method; create Entity from JSON
| Entity.from_row(data, feed) | Class method; create Entity from CSV row

## Validating a Feed

This library contains a basic GTFS validator. It validates required and optional attributes and their values, foreign keys, and requirements such as stop sequences.

Additionally, a wrapper to Google's Transitfeed `feedvalidator.py` is provided, if it is available on your system. This provides additional checks, as well as warnings for common feed problems such as date ranges, stop spacing, bus speeds, etc. However, this is currently only supported on zip'd feeds; if you have made any changes, you will have to write out a zip file first.

```
>>> import mzgtfs.feed
>>> import mzgtfs.validation
>>> report = mzgtfs.validation.ValidationReport()
>>> gtfs_feed = mzgtfs.feed.Feed('current.zip')
>>> gtfs_feed.validate(validator=report)
>>> gtfs_feed.validate_feedvalidator(validator=report)
>>> report.report()
Validation report:
<Feed .//mzgtfs/examples/sample-feed.zip>: Errors reported by feedvalidator.py; see report.html for details
```

## Writing data

Writing out GTFS CSV files and creating new zip archives is also supported.

```
>>> import mzgtfs.feed
>>> gtfs_feed = mzgtfs.feed.Feed('original.zip')
>>> for stop in gtfs_feed.stops(): stop.set('zone_id', '1')
>>> # Write out a stops.txt table with our updated stops, sorting on 'stop_id'
>>> gtfs_feed.write('stops.txt', gtfs_feed.stops(), sortkey='stop_id')
>>> # Create "new.zip", merging our stops table and the original feed.
>>> gtfs_feed.make_zip('new.zip', files=['stops.txt'], clone='original.zip')
```

## Contributing

Please [open a Github issue](https://github.com/transitland/mapzen-gtfs/issues/new) with as much of the following information as you're able to specify, or [contact us](#contact) for assistance.

## Contact

Transitland is sponsored by [Mapzen](http://mapzen.com). Contact us with your questions, comments, or suggests: [hello@mapzen.com](mailto:hello@mapzen.com).
