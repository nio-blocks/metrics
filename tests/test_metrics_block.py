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
