"""
blackbird aerospike module

IMPORTANT
 - please install "aerospike-tools" or citrusleaf python module.
"""

__VERSION__ = '0.1.1'

import types
import sys

from blackbird.plugins import base

# add aerospike python library path
sys.path.append('/opt/aerospike/lib/python')

try:
    # pylint: disable=import-error
    import citrusleaf
except ImportError:
    raise base.BlackbirdPluginError(
        'citrusleaf.py not in your python path.'
    )


class ConcreteJob(base.JobBase):
    """
    This class is Called by "Executor".
    Get aeropike information and send to specified zabbix server.
    """

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

    def build_items(self):
        """
        main loop
        """

        # ping item
        self.ping()

        # get build
        self._as_build()

        # get config
        self._as_config()

        # get latency
        self._as_latency()

        # get namespace statistics
        self._as_namespace_stat()

        # get node id
        self._as_node()

        # get services
        self._as_services()

        # get services-alumni
        self._as_services_alumni()

        # get statistics
        self._as_statistics()

    def build_discovery_items(self):
        """
        main loop for lld
        """

        # discovery namespaces
        self._lld_namespaces()

        # discovery sets
        self._lld_sets()

    def ping(self):
        """
        send ping item
        """

        self._enqueue('blackbird.aerospike.ping', 1)
        self._enqueue('blackbird.aerospike.version', __VERSION__)

    def _as_connect(self, cmd=None):
        """
        connect and return value
        """

        _user = None
        _password = None

        if self.options['aspass'] and self.options['asuser']:
            _user = self.options['asuser']
            _password = citrusleaf.hashpassword(self.options['aspass'])

        _conn = citrusleaf.citrusleaf_info(
            self.options['ashost'],
            self.options['asport'],
            cmd,
            _user,
            _password
        )

        if type(_conn) != types.StringType:
            raise base.BlackbirdPluginError(
                'request failed to {ashost}:{asport} ({cmd})'
                ''.format(
                    ashost=self.options['ashost'],
                    asport=self.options['asport'],
                    cmd=cmd
                )
            )

        return _conn

    def _as_build(self):
        """
        get build version
        """

        self._enqueue(
            'aerospike.asinfo.build',
            self._as_connect(cmd='build')
        )

    def _as_config(self):
        """
        get configuration value
        """

        _data = self._as_connect(cmd='get-config')

        for _sk, _sv in self._split_into_dict(_data).items():
            self._enqueue(
                'aerospike.asinfo.config[{sk}]'.format(sk=_sk), _sv
            )

    def _as_statistics(self):
        """
        get statistics
        """

        _data = self._as_connect(cmd='statistics')

        for _sk, _sv in self._split_into_dict(_data).items():
            self._enqueue(
                'aerospike.asinfo.statistics[{sk}]'.format(sk=_sk), _sv
            )

    def _as_latency(self):
        """
        get latency
        """

        histgrams = [
            'reads', 'writes_master', 'writes_reply', 'proxy', 'udf', 'query'
        ]

        for histgram in histgrams:
            _item_key = 'aerospike.asinfo.latency.{hst}'.format(hst=histgram)
            _cmd = 'latency:{hst}'.format(hst=histgram)
            _data = self._as_connect(cmd=_cmd).split(';')
            _ops = zip(_data[0].split(',')[1:], _data[1].split(',')[1:])

            for _key, _val in _ops:
                self._enqueue(
                    '{item_key}[{key}]'.format(item_key=_item_key, key=_key),
                    _val
                )

    def _get_as_namespaces(self):
        """
        return namespace list
        """

        return self._as_connect(cmd='namespaces').split(';')

    def _get_as_sets(self, namespace=None):
        """
        return sets list in namespace
        """

        _sets = []

        _cmd = 'sets/{namespace}'.format(namespace=namespace)
        _data = self._as_connect(cmd=_cmd).split(';')
        for _line in _data:
            if _line == '':
                continue
            for _values in _line.split(':'):
                _key, _value = _values.split('=')
                if _key == 'set_name':
                    _sets.append(_value)

        return _sets

    def _as_namespace_stat(self):
        """
        get namespace statistics
        """

        for _ns in self._get_as_namespaces():

            # namespace information
            _cmd = 'namespace/{ns}'.format(ns=_ns)
            _ns_stat = self._as_connect(cmd=_cmd)
            self.logger.debug(_ns_stat)
            for _key, _val in self._split_into_dict(_ns_stat).items():
                _item_key = (
                    'aerospike.asinfo.namespace[{ns},{key}]'
                    ''.format(ns=_ns, key=_key)
                )
                self._enqueue(_item_key, _val)

            # sets in namespace information
            _cmd = 'sets/{ns}'.format(ns=_ns)
            _set_count = 0
            for _sets in self._as_connect(cmd=_cmd).split(';'):

                if _sets == '':
                    continue

                _set_count += 1
                _field = _sets.split(':')
                _ns_name = _field[0].split('=')[1]
                _set_name = _field[1].split('=')[1]

                for _line in _field[2:]:
                    _key, _val = _line.split('=')
                    _item_key = (
                        'aerospike.asinfo.sets[{ns},{set},{key}]'
                        ''.format(ns=_ns_name, set=_set_name, key=_key)
                    )
                    self._enqueue(_item_key, _val)

            # send number of sets in namespace
            _key = 'aerospike.asinfo.namespace[{ns},number_of_sets]'.format(
                ns=_ns
            )
            self._enqueue(_key, _set_count)

            # bins in namespace information
            _cmd = 'bins/{ns}'.format(ns=_ns)
            _bins = self._as_connect(cmd=_cmd).split(',')
            self._enqueue(
                'aerospike.asinfo.bins[{ns},num-bin-names]'.format(ns=_ns),
                _bins[0].split('=')[1]
            )
            self._enqueue(
                'aerospike.asinfo.bins[{ns},bin-names-quota]'.format(ns=_ns),
                _bins[1].split('=')[1]
            )

    def _as_node(self):
        """
        get node id
        """

        self._enqueue(
            'aerospike.asinfo.nodeid',
            self._as_connect(cmd='node')
        )

    def _as_services(self):
        """
        get services information
        """

        self._enqueue(
            'aerospike.asinfo.services',
            self._as_connect(cmd='services')
        )

    def _as_services_alumni(self):
        """
        get services-alumni information
        """

        self._enqueue(
            'aerospike.asinfo.services-alumni',
            self._as_connect(cmd='services-alumni')
        )

    def _lld_namespaces(self):
        """
        discovery namespaces
        """

        self._enqueue_lld(
            'aerospike.namespaces.LLD',
            [{'{#NAMESPACE}': _ns} for _ns in self._get_as_namespaces()]
        )

    def _lld_sets(self):
        """
        discovery namespaces
        """

        _set_list = []

        for _namespace in self._get_as_namespaces():
            for _set in self._get_as_sets(_namespace):
                _set_list.append({'{#NAMESPACE}': _namespace, '{#SET}': _set})

        self._enqueue_lld('aerospike.sets.LLD', _set_list)

    def _enqueue(self, key, value):
        """
        enqueue item
        """

        item = ASItem(
            key=key,
            value=value,
            host=self.options['hostname']
        )
        self.queue.put(item, block=False)
        self.logger.debug(
            'Inserted to queue {key}:{value}'
            ''.format(key=key, value=value)
        )

    def _enqueue_lld(self, key, value):
        """
        enqueue lld item
        """

        item = base.DiscoveryItem(
            key=key,
            value=value,
            host=self.options['hostname']
        )
        self.queue.put(item, block=False)
        self.logger.debug(
            'Inserted to lld queue {key}:{value}'
            ''.format(key=key, value=str(value))
        )

    @staticmethod
    def _split_into_dict(_str):
        """
        aaa=bbb;ccc=ddd;...
        to
        {"aaa":"bbb", "ccc":"ddd", ... }
        """

        _dict = dict()
        for _line in str(_str).split(';'):
            if _line == '':
                continue

            # "asinfo -v namespace/<memory ns>" gets corrupt output ..
            try:
                _key, _value = _line.split('=')
                _dict[_key] = _value
            except ValueError:
                pass

        return _dict


# pylint: disable=too-few-public-methods
class ASItem(base.ItemBase):
    """
    Aerospike Item Class
    """

    def __init__(self, key, value, host):
        super(ASItem, self).__init__(key, value, host)

        self._data = {}
        self._generate()

    @property
    def data(self):
        return self._data

    def _generate(self):
        self._data['key'] = self.key
        self._data['value'] = self.value
        self._data['host'] = self.host
        self._data['clock'] = self.clock


class Validator(base.ValidatorBase):
    """
    Validate configuration.
    """

    def __init__(self):
        self.__spec = None

    @property
    def spec(self):
        self.__spec = (
            "[{0}]".format(__name__),
            "ashost=string(default='127.0.0.1')",
            "asport=integer(0, 65535, default=3000)",
            "asuser=string(default=None)",
            "aspass=string(default=None)",
            "hostname=string(default={0})".format(self.detect_hostname()),
        )
        return self.__spec
