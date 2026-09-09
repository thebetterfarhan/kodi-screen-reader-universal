# -*- coding: utf-8 -*-
"""Single-threaded, interruptible Tolk backend for active screen readers."""
import ctypes
import os
import threading
import time
import queue as Queue

from lib import util
from base import ThreadedTTSBackend


def _native_directory():
    return os.path.join(os.path.dirname(__file__), 'tolk')


class TolkTTSBackend(ThreadedTTSBackend):
    provider = 'tolk'
    displayName = 'Tolk (active screen reader)'
    settings = None
    interval = 40  # Existing user override settings still take precedence.
    _SILENCE = object()

    def __init__(self):
        self.dll = None
        self._ready = threading.Event()
        self._loaded_on_speech_thread = False
        self._queue_lock = threading.RLock()
        self.protectedQueue = Queue.Queue()
        self._generation = 0
        self._cancel_event = threading.Event()
        self._reader_ready = False
        self._reader_name = None
        self._next_reader_probe = 0.0
        self._reader_backoff = 0.5
        self._reader_backoff_max = 5.0
        self._last_reader_log = 0.0
        self._deferred = None
        ThreadedTTSBackend.__init__(self)

    @staticmethod
    def available():
        return util.isWindows() and os.path.isfile(os.path.join(_native_directory(), 'Tolk.dll'))

    def init(self):
        native = _native_directory()
        try:
            self._reader_backoff_max = max(1.0, float(util.getSetting('reader_reconnect_max', 5)))
            os.environ['PATH'] = native + ';' + os.environ.get('PATH', '')
            try:
                os.add_dll_directory(native)
            except (AttributeError, OSError):
                pass
            # Tolk.h declares TOLK_CALL as __cdecl, so CDLL is required.
            self.dll = ctypes.CDLL(os.path.join(native, 'Tolk.dll'))
            self.dll.Tolk_TrySAPI.argtypes = [ctypes.c_bool]
            self.dll.Tolk_TrySAPI.restype = None
            self.dll.Tolk_Load.argtypes = []
            self.dll.Tolk_Load.restype = None
            self.dll.Tolk_IsLoaded.argtypes = []
            self.dll.Tolk_IsLoaded.restype = ctypes.c_bool
            self.dll.Tolk_Unload.argtypes = []
            self.dll.Tolk_Unload.restype = None
            self.dll.Tolk_Output.argtypes = [ctypes.c_wchar_p, ctypes.c_bool]
            self.dll.Tolk_Output.restype = ctypes.c_bool
            self.dll.Tolk_Silence.argtypes = []
            self.dll.Tolk_Silence.restype = ctypes.c_bool
            self.dll.Tolk_DetectScreenReader.argtypes = []
            self.dll.Tolk_DetectScreenReader.restype = ctypes.c_wchar_p
            self.dll.Tolk_HasSpeech.argtypes = []
            self.dll.Tolk_HasSpeech.restype = ctypes.c_bool
            util.LOG('Tolk universal screen-reader backend prepared')
        except Exception as exc:
            self.flagAsDead('Could not load Tolk: {0}'.format(exc))
            util.LOG('Tolk load error: {0}'.format(exc))
        finally:
            self._ready.set()

    def _emptyQueueLocked(self):
        try:
            while True:
                self.queue.get_nowait()
                self.queue.task_done()
        except Queue.Empty:
            return

    def _newGeneration(self, reason):
        """Cancel queued work and invalidate an in-flight pause atomically."""
        with self._queue_lock:
            self._generation += 1
            self._cancel_event.set()
            self._cancel_event = threading.Event()
            self._emptyQueueLocked()
            if not self._deferred or self._deferred[0] is not None:
                self._deferred = None
            generation = self._generation
            # The worker alone calls Tolk; silence precedes replacement speech.
            self.queue.put_nowait((self._SILENCE, generation, None, time.monotonic()))
        util.VERBOSE_LOG('Tolk cancel generation {0}: {1}'.format(generation, reason))
        return generation

    def _currentGeneration(self):
        with self._queue_lock:
            return self._generation, self._cancel_event

    def _enqueueText(self, text, generation):
        self.queue.put_nowait(('text', generation, text, time.monotonic()))
        util.VERBOSE_LOG('Tolk enqueue generation {0}'.format(generation))

    def _enqueuePause(self, milliseconds, generation=None):
        if not self.active:
            return
        if generation is None:
            generation, unused = self._currentGeneration()
        self.queue.put_nowait(('pause', generation, milliseconds, time.monotonic()))

    def say(self, text, interrupt=False):
        if not self.active:
            return
        if interrupt:
            generation = self._newGeneration('interrupting speech')
        else:
            generation, unused = self._currentGeneration()
        self._enqueueText(text, generation)

    def sayList(self, texts, interrupt=False):
        if not texts or not self.active:
            return
        if interrupt:
            generation = self._newGeneration('interrupting speech group')
        else:
            generation, unused = self._currentGeneration()
        for index, text in enumerate(texts):
            if index:
                self._enqueuePause(500, generation)
            self._enqueueText(text, generation)

    def sayProtected(self, text, interrupt=False):
        """Queue an explicit command/dialog without navigation discarding it."""
        if not self.active:
            return
        if interrupt:
            self._newGeneration('protected announcement')
        self.protectedQueue.put_nowait(('text', None, text, time.monotonic()))

    def sayProtectedList(self, texts, interrupt=False):
        if not texts or not self.active:
            return
        if interrupt:
            self._newGeneration('protected announcement group')
        for index, text in enumerate(texts):
            if index:
                self.protectedQueue.put_nowait(('pause', None, 500, time.monotonic()))
            self.protectedQueue.put_nowait(('text', None, text, time.monotonic()))

    def insertPause(self, ms=500):
        self._enqueuePause(ms)

    def _stop(self):
        if self.active:
            self._newGeneration('stop')

    def stop(self):
        self._stop()

    def isSpeaking(self):
        # Dispatch work, not a measurement of the reader's audible speech.
        return self.active and (self._threadedIsSpeaking or not self.queue.empty() or not self.protectedQueue.empty())

    def _nextItem(self):
        """Navigation is immediate; protected announcements resume afterward."""
        try:
            return self.queue.get(timeout=0.05), self.queue
        except Queue.Empty:
            try:
                return self.protectedQueue.get_nowait(), self.protectedQueue
            except Queue.Empty:
                raise

    def _pauseInterruptibly(self, milliseconds, generation, cancel_event):
        started = time.monotonic()
        if cancel_event.wait(milliseconds / 1000.0):
            util.VERBOSE_LOG('Tolk pause cancelled after {0:.1f}ms'.format((time.monotonic() - started) * 1000.0))
            return False
        return generation == self._currentGeneration()[0]

    def _logReaderUnavailable(self, detail):
        now = time.monotonic()
        if now - self._last_reader_log >= 5.0:
            util.LOG('Tolk screen reader unavailable ({0}); retrying without SAPI'.format(detail))
            self._last_reader_log = now

    def statusText(self):
        if self.dead:
            return 'Tolk error: {0}'.format(self.deadReason or 'unavailable')
        if self._reader_ready and self._reader_name:
            return 'Tolk connected to {0}. SAPI fallback is off.'.format(self._reader_name)
        if self._loaded_on_speech_thread:
            return 'Tolk is loaded. No speech-capable screen reader is active. SAPI fallback is off.'
        return 'Tolk is starting. SAPI fallback is off.'

    def _ensureReaderReady(self):
        """Probe on the worker thread with bounded backoff; never use SAPI."""
        now = time.monotonic()
        if self._reader_ready:
            return True
        if now < self._next_reader_probe:
            return False
        reader = self.dll.Tolk_DetectScreenReader()
        has_speech = bool(self.dll.Tolk_HasSpeech())
        if reader and has_speech:
            self._reader_ready = True
            self._reader_name = reader
            self._reader_backoff = 0.5
            util.LOG('Tolk active screen reader: {0}'.format(reader))
            return True
        self._next_reader_probe = now + self._reader_backoff
        self._reader_backoff = min(self._reader_backoff * 2.0, self._reader_backoff_max)
        self._reader_name = None
        self._logReaderUnavailable('no active speech-capable reader')
        return False

    def _deferLatest(self, generation, value, queued_at):
        if generation is None or generation == self._currentGeneration()[0]:
            self._deferred = (generation, value, queued_at)

    def _dispatchText(self, generation, value, queued_at):
        if generation is not None and generation != self._currentGeneration()[0]:
            return
        if not self._ensureReaderReady():
            self._deferLatest(generation, value, queued_at)
            return
        # Re-check immediately before dispatch to avoid stale labels.
        if generation is not None and generation != self._currentGeneration()[0]:
            return
        self._threadedIsSpeaking = True
        dispatch_ms = (time.monotonic() - queued_at) * 1000.0
        util.VERBOSE_LOG('Tolk dispatch latency: {0:.1f}ms'.format(dispatch_ms))
        if not self.dll.Tolk_Output(str(value), False):
            self._reader_ready = False
            self._reader_name = None
            self._deferLatest(generation, value, queued_at)
            self._logReaderUnavailable('output failed')
        elif self._deferred and self._deferred[0] == generation:
            self._deferred = None
        self._threadedIsSpeaking = False

    def _handleQueue(self):
        util.LOG('Tolk speech thread started')
        self._ready.wait(10)
        try:
            if not self.dll:
                return
            # Keep SAPI disabled; use the active screen reader through Tolk.
            self.dll.Tolk_TrySAPI(False)
            self.dll.Tolk_Load()
            if not self.dll.Tolk_IsLoaded():
                self.flagAsDead('Tolk could not initialize')
                util.LOG('Tolk_Load completed but Tolk_IsLoaded is false')
                return
            self._loaded_on_speech_thread = True
            self._ensureReaderReady()
            while self.active and not util.abortRequested():
                try:
                    item, source_queue = self._nextItem()
                    kind, generation, value, queued_at = item
                    source_queue.task_done()
                    current_generation, cancel_event = self._currentGeneration()
                    if kind == 'shutdown':
                        self.dll.Tolk_Silence()
                        self.active = False
                        break
                    if kind is self._SILENCE:
                        self.dll.Tolk_Silence()
                        util.VERBOSE_LOG('Tolk silence dispatched')
                        continue
                    if generation is not None and generation != current_generation:
                        continue
                    if kind == 'pause':
                        self._pauseInterruptibly(value, generation, cancel_event)
                        continue
                    if kind == 'text' and value:
                        self._dispatchText(generation, value, queued_at)
                except Queue.Empty:
                    if self._deferred:
                        self._dispatchText(*self._deferred)
                except Exception as exc:
                    self._threadedIsSpeaking = False
                    self.flagAsDead('Tolk speech error: {0}'.format(exc))
                    util.LOG('Tolk speech error: {0}'.format(exc))
                    return
        finally:
            if self._loaded_on_speech_thread:
                try:
                    self.dll.Tolk_Unload()
                except Exception:
                    pass
            util.LOG('Tolk speech thread finished')

    def _close(self):
        if not self.active:
            return
        generation = self._newGeneration('close')
        # Let the speech worker perform the final Tolk_Silence and unload.
        self.queue.put_nowait(('shutdown', generation, None, time.monotonic()))
        if self.thread is not threading.current_thread():
            self.thread.join(1.0)
        self.active = False
        self._emptyQueue()
        try:
            while True:
                self.protectedQueue.get_nowait()
                self.protectedQueue.task_done()
        except Queue.Empty:
            pass
