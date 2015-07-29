from unittest.mock import MagicMock
from collections import defaultdict
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.modules.threading import Event
from ..metrics_block import Metrics


class EventMetrics(Metrics):

    def __init__(self, e):
        super().__init__()
        self._e = e

    def _collect_and_notify(self):
        super()._collect_and_notify()
        self._e.set()

class TestMetricsBlock(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        # This will keep a list of signals notified for each output
        self.last_notified = defaultdict(list)
        self.expected = [
            'cpu_percentage',
            'virtual_memory',
            'swap_memory',
            'disk_usage',
            'disk_io_counters',
            'net_io_counters'
        ]

    def signals_notified(self, signals, output_id='default'):
        self.last_notified[output_id].extend(signals)

    def test_generate_metrics(self):
        event = Event()
        blk = EventMetrics(event)
        self.configure_block(blk, {
            "interval": {
                "milliseconds": 500
            }
        })
        blk.start()
        event.wait(1)
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertTrue('default' in self.last_notified)
        for k in self.last_notified['default'][0].to_dict():
            for idx, f in enumerate(self.expected):
                if k.startswith(f):
                    break
                elif idx == len(self.expected)-1:
                    raise AssertionError("Unexpected report key '%s'" % k)

    def test_sensors(self):
        event = Event()
        blk = EventMetrics(event)
        self.configure_block(blk, {
            "menu": {
                "sensors": True,
                "cpu_perc": False,
                "virtual_mem": False,
                "swap_mem": False,
                "disk_usage": False,
                "disk_io_ct": False,
                "net_io_ct": False
            },
            "interval": {
                "milliseconds": 500
            }
        })
        blk._subprocess_command = MagicMock(
            return_value=self._sample_sensors_output())
        print(blk._subprocess_command)
        blk.start()
        event.wait(1)
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertTrue('default' in self.last_notified)
        self.assertDictEqual(self.last_notified['default'][0].to_dict(),
                             {'sensors_Core 0': 42.0,
                              'sensors_Core 1': 42.0,
                              'sensors_Core 2': 41.0,
                              'sensors_Core 3': 41.0,
                              'sensors_temp1': 26.8})

    def _sample_sensors_output(self):
        '''
        cpitz-virtual-0
        Adapter: Virtual device
        temp1:        +26.8°C  (crit = +90.0°C)

        coretemp-isa-0000
        Adapter: ISA adapter
        Core 0:       +42.0°C  (high = +105.0°C, crit = +105.0°C)
        Core 1:       +42.0°C  (high = +105.0°C, crit = +105.0°C)
        Core 2:       +41.0°C  (high = +105.0°C, crit = +105.0°C)
        Core 3:       +41.0°C  (high = +105.0°C, crit = +105.0°C)
        '''
        return ('acpitz-virtual-0\n,'
                'Adapter: Virtual device\n'
                'temp1:        +26.8°C  (crit = +90.0°C)\n\n'
                'coretemp-isa-0000\n'
                'Adapter: ISA adapter\n'
                'Core 0:       +42.0°C  (high = +105.0°C, crit = +105.0°C)\n'
                'Core 1:       +42.0°C  (high = +105.0°C, crit = +105.0°C)\n'
                'Core 2:       +41.0°C  (high = +105.0°C, crit = +105.0°C)\n'
                'Core 3:       +41.0°C  (high = +105.0°C, crit = +105.0°C)')
