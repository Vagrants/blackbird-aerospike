blackbird-aerospike
===================

[![Build Status](https://travis-ci.org/Vagrants/blackbird-aerospike.png?branch=development)](https://travis-ci.org/Vagrants/blackbird-aerospike)

Get Aerospike information.

* `asinfo -v namespace/<ns>`
* `asinfo -v latency`
* `asinfo -v sets/<set>`
* `asinfo -v get-config`
* and more

## adding monitoring user for blackbird-aerospike

If your aerospike cluster is set `enable-security true`, you need to create user for monitoring.  
This is example for creating `monitor` user.

```sql
aql> CREATE USER monitor PASSWORD monitor ROLES read
```

and set `/etc/blackbird/conf.d/aerospike.cfg` like this.

```
asuser = monitor
aspass = monitor
```

## low level discovery

`blackbird-aerospike` module discovers namespace and set.

## attention

This module needs `citrusleaf` python module.  
So please install `aerospike-tools` or place `citrusleaf.py` to your python `sys.path`.

`aerospike-tools` places `daemon.py` to `/opt/aerospike/lib/python/`, so `python-daemon` conflicts this aerospike's daemon.py.  
Please rename `/opt/aerospike/lib/python/daemon.py` for running blackbird.





