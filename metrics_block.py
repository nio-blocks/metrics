import psutil

from nio.common.block.base import Block
from nio.common.signal.base import Signal
from nio.common.command import command
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.object import ObjectProperty
from nio.metadata.properties.holder import PropertyHolder
from nio.metadata.properties.bool import BoolProperty
from nio.metadata.properties.timedelta import TimeDeltaProperty
from nio.modules.scheduler import Job


RETRY_LIMIT = 3


class Menu(PropertyHolder):
    
    cpu_perc = BoolProperty(title='CPU Percentage', default=True)
    virtual_mem = BoolProperty(title='Virtual Memory', default=True)
    swap_mem = BoolProperty(title='Swap Memory', default=True)
    disk_usage = BoolProperty(title='Disk Usage', default=True)
    disk_io_ct = BoolProperty(title='Disk I/O Stats', default=True)
    net_io_ct = BoolProperty(title='Network I/O Stats', default=True)

    # a fairly long list in the general case. not included by default
    pids = BoolProperty(title='Process Identifiers')

    # this requires superuser priviledges and dumps a whole ton of
    # data. Maybe unnecessary? Not included by default
    skt_conns = BoolProperty(title='Socket Connections')


@command('report')
@Discoverable(DiscoverableType.block)
class Metrics(Block):
    
    menu = ObjectProperty(Menu, title='Menu')
    interval = TimeDeltaProperty(title='Interval')

    def __init__(self):
        super().__init__()
        self._metrics_job = None
        self._retry_count = 0

    def start(self):
        self._metrics_job = Job(
            self._collect_and_notify,
            self.interval,
            True
        )

    def stop(self):
        if self._metrics_job is not None:
            self._metrics_job.cancel()

    def report(self):
        return self._collect_stats()

    def _collect_and_notify(self):
        stats = self._collect_stats()
        if stats:
            self.notify_signals([Signal(stats)])

    def _collect_stats(self):
        result = {}

        try:
            # CPU usage statistics
            if self.menu.cpu_perc:
                base = 'cpu_percentage'
                fields = ['overall', 'per_cpu']
                for idx, f in enumerate(fields):
                    data = psutil.cpu_percent(percpu=bool(idx))
                    result["{0}_{1}".format(base,f)] = data
         
            # Virtual memory usage
            if self.menu.virtual_mem:
                self._collect_results('virtual_memory', result)

            # Swap memory usage
            if self.menu.swap_mem:
                self._collect_results('swap_memory', result)
                # result['swap_memory'] = psutil.swap_memory()._asdict()

            # Disk usage
            if self.menu.disk_usage:
                self._collect_results('disk_usage', result, ['/'])
            
            # Disk I/O statistics
            if self.menu.disk_io_ct:
                self._collect_results('disk_io_counters', result)
            
            # Net I/O statistics
            if self.menu.net_io_ct:
                self._collect_results('net_io_counters', result)

            # Process IDs - this dumps a big list and is disabled by default
            if self.menu.pids:
                result['process_identifiers'] = psutil.pids()

            # Socket Connections - dumps a big list and requires superuser
            # also disabled by default. Dumps a list of dictionaries; this
            # approach won't look very nice in the database, but is generally
            # quite long and not usually used.
            if self.menu.skt_conns:
                result['network_connections'] = \
                    [self.native_dict(skt._asdict()) \
                     for skt in psutil.net_connections()]

        except Exception as e:
            self._logger.error(
                "While processing system metrics: {0}".format(str(e))
            )
            if self._retry_count < RETRY_LIMIT:
                self._retry_count += 1
                return self._collect_stats()
            else:
                self._logger.error(
                    "System report failed {0} times, aborting...".format(
                        RETRY_LIMIT)
                )
                self._retry_count = 0
                return None
        else:
            self._retry_count = 0
            return result

    def _collect_results(self, base, result, args=[]):
        ''' Helper function to flatten the data for each psutil result

        '''
        data = getattr(psutil, base)(*args)._asdict()
        for f in data.keys():
            result['{0}_{1}'.format(base,f)] = data[f]

    def native_dict(self, obj):
        return {k: obj[k] for k in obj}
