import os
from ..process_metrics_block import ProcessMetrics
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.modules.threading import Event
from nio.common.signal.base import Signal


class EventProcessMetrics(ProcessMetrics):
    
    def __init__(self, e):
        super().__init__()
        self._e = e

    def process_signals(self, signals):
        super().process_signals(signals)
        self._e.set()


class TestProcessMetrics(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        self.report = None
        self.expected = [
            'cpu_percentage',
            'virtual_memory',
            'num_ctx_switches',
            'memory_percent',
            'num_fds',
            'is_running',
            'pid'
        ]

    def signals_notified(self, signals, output_id='default'):
        self.report = signals[0]

    def test_generate_metrics(self):
        event = Event()
        blk = EventProcessMetrics(event)
        self.configure_block(blk, {
            'pid_expr': "{{$pid}}"
        })
        the_pid = os.getpid()
        blk.start()
        blk.process_signals([Signal({'pid': the_pid})])
        event.wait(1)
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertIsNotNone(self.report)

        for k in self.report.to_dict():
            for idx, f in enumerate(self.expected):
                if k.startswith(f):
                    break
                elif idx == len(self.expected)-1:
                    raise AssertionError("Unexpected report key '%s'" % k)
                
