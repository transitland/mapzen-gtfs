# Mapzen GTFS

[![Circle CI](https://circleci.com/gh/transitland/mapzen-gtfs.png?style=badge)](https://circleci.com/gh/transitland/mapzen-gtfs)

A simple GTFS library. 

Supports reading individual GTFS tables, or constructing a graph to represent each agency in a feed.

## Installation

Installation using pip:

```
pip install mzgtfs
```

Alternatively, [download from PyPi](https://pypi.python.org/pypi/mzgtfs) or clone this repository, and install using setup.py:

```
python ./setup.py install
```

The dependencies [mzgeohash](https://github.com/transitland/mapzen-geohash) and [unicodecsv](https://pypi.python.org/pypi/unicodecsv) will be automatically installed using the above methods.

## Reading tables

```
>>> import mzgtfs.feed
>>> f = mzgtfs.feed.Feed('current.zip')
>>> f.read('routes') # List
[<mzgtfs.entities.Route object at 0x10df47590>, <mzgtfs.entities.Route object at 0x10df47890>, <mzgtfs.entities.Route object at 0x10df478d0>, <mzgtfs.entities.Route object at 0x10df47910>, <mzgtfs.entities.Route object at 0x10df47950>, <mzgtfs.entities.Route object at 0x10df479d0>]
>>> f.iterread('routes') # Generator
<generator object iterread at 0x10ea6c690>
>>> f.route(id='05').name()
u'Fremont - Daly City'
```

## Working with an Agency

Many GTFS contain multiple agencies. You can construct a graph for each agency that includes only the relevant routes, stops, etc., by calling preload(). This can then be searched, or exported using json().

```
>>> f.agencies()
[<mzgtfs.entities.Agency object at 0x105b99dd0>]
>>> bart = f.agency(id='BART')
<mzgtfs.entities.Agency object at 0x10df3be10>
>>> bart.preload()
>>> len(bart.routes())
6
>>> len(bart.trips())
2528
>>> len(bart.stops())
47
>>> bart.route(id='05').name()
u'Fremont - Daly City'
>>> bart.stop('EMBR').name()
u'Embarcadero'
>>> bart.json() # dict suitable for json.dump()
{'name': u'Bay Area Rapid Transit', ...}
```

## Entities

Classes are currently provided for the following entities:

	* Agency
	* Route
	* Trip
	* StopTime
	* Stop

## Contributing

Please [open a Github issue](https://github.com/transitland/mapzen-gtfs/issues/new) with as much of the following information as you're able to specify, or [contact us](#contact) for assistance.

## License

Unless otherwise indicated, the code used to build and maintain this registry is Copyright (C) 2014-2015 Mapzen and released under the [MIT license](http://opensource.org/licenses/MIT).

## Contact

Transitland is sponsored by [Mapzen](http://mapzen.com). Contact us with your questions, comments, or suggests: [hello@mapzen.com](mailto:hello@mapzen.com).