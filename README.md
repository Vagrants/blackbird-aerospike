blackbird-aerospike
===================

[![Build Status](https://travis-ci.org/Vagrants/blackbird-aerospike.png?branch=development)](https://travis-ci.org/Vagrants/blackbird-aerospike)

Get Aerospike information.

* `asinfo -v namespace/<ns>`
* `asinfo -v latency`
* `asinfo -v sets/<set>`
* `asinfo -v get-config`
* and more

## attention

This module needs `citrusleaf` python module.  
So please install `aerospike-tools` or place `citrusleaf.py` to your python `sys.path`.

`aerospike-tools` places `daemon.py` to `/opt/aerospike/lib/python/`, so `python-daemon` conflicts this aerospike's daemon.py.  
Please rename `/opt/aerospike/lib/python/daemon.py` for running blackbird.





