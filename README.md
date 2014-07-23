# OpenKVK: API wrapper
[![pypi](http://img.shields.io/pypi/v/OpenKVK.svg)](https://pypi.python.org/pypi/OpenKVK/)
[![Build Status](https://travis-ci.org/jeff-99/OpenKVK.svg?branch=development)](https://travis-ci.org/jeff-99/OpenKVK)
[![License](http://img.shields.io/pypi/l/OpenKVK.svg)](https://pypi.python.org/pypi/OpenKVK/)
## What is it ?

OpenKVK is an UNOFFICIAL python wrapper for the [openkvk API](https://openkvk.nl/api.html)

## Main Features
a few of the things this library does well:

- Get dutch company information by name or kvk-number
- Get lists of companies based on sbi-codes, location or both
- Output information in `json`, `csv` or `dict`
- Wrap your own queries with or without result parsing

## Command line interface
For quick access to the openkvk api you could use the OpenKVK CLI, like so:

```sh
openkvk --help
openkvk --kvk 27312152 --format json --output test.json
```

## Installation
The source code is currently hosted on GitHub at:
http://github.com/jeff-99/OpenKVK

Install via `pip`:

```sh
pip install OpenKVK
```

And via `easy_install`:

```sh
easy_install OpenKVK
```

## Example

First you need to instantiate a OpenKVK client
```python
from OpenKVKimport ApiClient

client = ApiClient()

```
The Client returns data as python dicts, to change this output format.
you could do one of the following

```python
client = ApiClient('json')
```
OR
```python
client.setResponseFormat('json')
```

The client can then be used to query by using the following:

```python
client.get_by_kvk(53012321)
client.get_by_city('Rotterdam')
client.get_by_name('KPN')
client.get_by_sbi('06.10')
```

The `city`, `name` and `sbi` functions also accept a maximum number of results (defaults to 99)
and a additional filters, like:

```python
client.get_by_sbi('06.10',limit=150, plaats="Rotterdam")
```

for a full list of available filters check [openkvk](https://www.openkvk.nl/api.html)

If you like to construct you own SQL-queries and you like the results to be parsed to a valid JSON array, a python list of dicts or a valid csv
you could use the `QueryBuilder` class.

```python
from OpenKVK import QueryBuilder

client = QueryBuilder()
client.setResponseFormat('csv')
client.query("SELECT * FROM kvk WHERE kvks = 27312152")
```

If you don't want the parsed results there is also a very minimalistic api client

```python
from OpenKVK import BaseClient

client = BaseClient()
client.setResponseFormat('py')
client.query("SELECT * FROM kvk WHERE kvks = 27312152")

## License
MIT


