"""Mocked unit tests for Tolk queue cancellation; run with Python 3.8+."""
import importlib.util
import os
import queue
import sys
import threading
import time
import types
import unittest


def load_tolk():
    util = types.ModuleType('lib.util')
    util.isWindows = lambda: True
    util.abortRequested = lambda: False
    util.LOG = lambda *args: None
    util.VERBOSE_LOG = lambda *args: None
    lib = types.ModuleType('lib')
    lib.util = util
    base = types.ModuleType('base')
    class FakeThreadedTTSBackend(object):
        def _emptyQueue(self):
            try:
                while True:
                    self.queue.get_nowait()
                    self.queue.task_done()
            except queue.Empty:
                pass
    base.ThreadedTTSBackend = FakeThreadedTTSBackend
    sys.modules.update({'lib': lib, 'lib.util': util, 'base': base})
    path = os.path.join(os.path.dirname(__file__), '..', 'addon', 'service.xbmc.tts', 'lib', 'backends', 'tolk.py')
    spec = importlib.util.spec_from_file_location('tolk_under_test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.TolkTTSBackend


TolkTTSBackend = load_tolk()


def bare_backend():
    backend = TolkTTSBackend.__new__(TolkTTSBackend)
    backend.active = True
    backend.queue = queue.Queue()
    backend.protectedQueue = queue.Queue()
    backend._queue_lock = threading.RLock()
    backend._generation = 0
    backend._cancel_event = threading.Event()
    backend._deferred = None
    backend._reader_ready = True
    backend._reader_name = 'Mock reader'
    backend._threadedIsSpeaking = False
    backend._ready = threading.Event()
    backend._ready.set()
    backend._loaded_on_speech_thread = False
    backend._next_reader_probe = 0.0
    backend._reader_backoff = 0.5
    backend._reader_backoff_max = 5.0
    backend._last_reader_log = 0.0
    return backend


def start_fake_worker():
    backend = bare_backend()
    calls = []
    worker_id = []
    def record(name, result=None):
        calls.append(name)
        worker_id.append(threading.get_ident())
        return result
    backend.dll = types.SimpleNamespace(
        Tolk_TrySAPI=lambda value: record('try_sapi'),
        Tolk_Load=lambda: record('load'),
        Tolk_IsLoaded=lambda: record('is_loaded', True),
        Tolk_DetectScreenReader=lambda: record('detect', 'Mock reader'),
        Tolk_HasSpeech=lambda: record('has_speech', True),
        Tolk_Silence=lambda: record('silence', True),
        Tolk_Output=lambda text, interrupt: record('output', True),
        Tolk_Unload=lambda: record('unload'))
    backend.thread = threading.Thread(target=backend._handleQueue)
    backend.thread.start()
    deadline = time.monotonic() + 1.0
    while 'load' not in calls and time.monotonic() < deadline:
        time.sleep(0.005)
    return backend, calls, worker_id


class TolkQueueTests(unittest.TestCase):
    def test_interrupt_cancels_a_500ms_pause_without_waiting_for_it(self):
        backend = bare_backend()
        generation, event = backend._currentGeneration()
        result = []
        worker = threading.Thread(target=lambda: result.append(backend._pauseInterruptibly(500, generation, event)))
        worker.start()
        time.sleep(0.02)
        backend._newGeneration('test navigation')
        worker.join(0.2)
        self.assertFalse(worker.is_alive())
        self.assertEqual(result, [False])

    def test_stale_text_enqueued_during_cancel_is_identified_by_generation(self):
        backend = bare_backend()
        old_generation, unused = backend._currentGeneration()
        backend._newGeneration('rapid direction change')
        backend._enqueueText('obsolete label', old_generation)
        kind, generation, value, unused = backend.queue.get_nowait()  # silence command
        self.assertIs(kind, backend._SILENCE)
        kind, generation, value, unused = backend.queue.get_nowait()
        self.assertEqual(kind, 'text')
        self.assertNotEqual(generation, backend._currentGeneration()[0])

    def test_newest_interrupting_label_replaces_pending_labels(self):
        backend = bare_backend()
        backend._enqueueText('first', 0)
        latest = backend._newGeneration('newest label')
        backend._enqueueText('latest', latest)
        items = [backend.queue.get_nowait(), backend.queue.get_nowait()]
        self.assertIs(items[0][0], backend._SILENCE)
        self.assertEqual(items[1][2], 'latest')

    def test_dispatch_does_not_output_when_generation_changes_before_call(self):
        backend = bare_backend()
        calls = []
        backend._ensureReaderReady = lambda: True
        backend.dll = types.SimpleNamespace(Tolk_Output=lambda text, interrupt: calls.append(text) or True)
        states = [(0, threading.Event()), (1, threading.Event())]
        backend._currentGeneration = lambda: states.pop(0)
        backend._threadedIsSpeaking = False
        backend._dispatchText(0, 'stale', time.monotonic())
        self.assertEqual(calls, [])

    def test_final_selection_is_the_only_live_generation(self):
        backend = bare_backend()
        for label in ('one', 'two', 'final'):
            generation = backend._newGeneration(label)
            backend._enqueueText(label, generation)
        live = []
        while not backend.queue.empty():
            item = backend.queue.get_nowait()
            if item[0] == 'text' and item[1] == backend._generation:
                live.append(item[2])
        self.assertEqual(live, ['final'])

    def test_non_interrupting_group_keeps_order_and_pauses(self):
        backend = bare_backend()
        backend.sayList(['dialog', 'message', 'button'], interrupt=False)
        items = [backend.queue.get_nowait() for unused in range(5)]
        self.assertEqual([item[0] for item in items], ['text', 'pause', 'text', 'pause', 'text'])
        self.assertEqual([items[0][2], items[2][2], items[4][2]], ['dialog', 'message', 'button'])

    def test_navigation_does_not_discard_protected_dialog(self):
        backend = bare_backend()
        backend.sayProtectedList(['dialog title', 'message'], interrupt=False)
        generation = backend._newGeneration('navigation')
        backend._enqueueText('new focus', generation)
        self.assertEqual(backend.protectedQueue.qsize(), 3)
        navigation = [backend.queue.get_nowait(), backend.queue.get_nowait()]
        self.assertIs(navigation[0][0], backend._SILENCE)
        self.assertEqual(navigation[1][2], 'new focus')

    def test_shutdown_serializes_silence_and_unload_on_worker(self):
        backend, calls, worker_ids = start_fake_worker()
        backend._close()
        self.assertFalse(backend.thread.is_alive())
        self.assertIn('silence', calls)
        self.assertEqual(calls[-1], 'unload')
        self.assertEqual(len(set(worker_ids)), 1)

    def test_backend_replacement_does_not_overlap_workers(self):
        first, calls, unused = start_fake_worker()
        first._close()
        self.assertFalse(first.thread.is_alive())
        second, calls, unused = start_fake_worker()
        self.assertTrue(second.thread.is_alive())
        second._close()
        self.assertFalse(second.thread.is_alive())


if __name__ == '__main__':
    unittest.main()
