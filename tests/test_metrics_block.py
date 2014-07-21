from metrics.metrics_block import Metrics
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.modules.threading.imports import Event


class EventMetrics(Metrics):
    
    def __init__(self, e):
        self._e = e

    def _collect_and_notify(self):
        super()._collect_and_notify()
        self._e.set()

class TestMetricsBlock(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        self.report = None
        self.expected_fields = [
            'cpu_percentage',
            'virtual_memory',
            'swap_memory',
            'disk_usage',
            'disk_io_counters',
            'net_io_counters'
        ]
    
    def signals_notified(self, signals):
        self.report = signals[0]

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
        self.assertIsNotNone(self.report)
        self.assertCountEqual(self.report.to_dict(), self.expected_fields)
        
        
        
        
        
                             