# OpenKVK: API wrapper

## What is it ?

OpenKVK is an UNOFFICIAL python wrapper for the [**openkvk API**][https://openkvk.nl/api.html]

## Installation
The source code is currently hosted on GitHub at:
http://github.com/jeff-99/OpenKVK

## Main Features
a few of the things this library does well:

- Get dutch company information by name or kvk-number
- Get lists of companies based on sbi-codes, location or both
- Output information in `json`, `csv` or `dict`


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
from OpenKVK.Client import Client

client = Client()

```
The Client returns data as python dicts, to change this output format.
you could do one of the following

```python
client = Client('json')
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
and a dictionary of additional filters, like:

```python
client.get_by_sbi('06.10',limit=150,filters={'plaats':'Rotterdam'})
```




## License
MIT


