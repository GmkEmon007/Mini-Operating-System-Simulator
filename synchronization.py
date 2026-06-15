"""
Module 4: Process Synchronization - Dining Philosophers Problem
Uses threading with locks (mutexes) to simulate forks as shared resources.

This module exposes a DiningPhilosophers simulation class that runs each
philosopher in its own thread. A GUI can poll `get_states()` and
`get_log()` to update its display, and call `start()`, `pause()`,
`resume()`, and `stop()` to control the simulation.
"""

import threading
import time
import random


THINKING = "Thinking"
HUNGRY = "Hungry"
EATING = "Eating"


class DiningPhilosophers:
    def __init__(self, num_philosophers=5, speed=1.0, log_callback=None):
        self.n = num_philosophers
        self.speed = speed  # multiplier: higher = faster
        self.forks = [threading.Lock() for _ in range(self.n)]
        self.states = [THINKING] * self.n
        self.state_lock = threading.Lock()
        self.log_callback = log_callback
        self.threads = []
        self._running = threading.Event()
        self._paused = threading.Event()
        self._paused.set()  # not paused initially
        self._stop_flag = threading.Event()

    # ------------------------------------------------------------------
    def _log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def _set_state(self, pid, state):
        with self.state_lock:
            self.states[pid] = state
        self._log(f"P{pid + 1} is {state}")

    def get_states(self):
        with self.state_lock:
            return list(self.states)

    # ------------------------------------------------------------------
    def _philosopher_life(self, pid):
        left = pid
        right = (pid + 1) % self.n

        # To avoid circular-wait deadlock, always acquire the
        # lower-numbered fork first.
        first, second = (left, right) if left < right else (right, left)

        while not self._stop_flag.is_set():
            self._paused.wait()
            if self._stop_flag.is_set():
                break

            # Thinking
            self._set_state(pid, THINKING)
            time.sleep(random.uniform(0.5, 1.5) / self.speed)

            self._paused.wait()
            if self._stop_flag.is_set():
                break

            # Hungry - try to acquire forks
            self._set_state(pid, HUNGRY)

            self.forks[first].acquire()
            self._log(f"P{pid + 1} picked up fork {first}")
            self.forks[second].acquire()
            self._log(f"P{pid + 1} picked up fork {second}")

            # Eating
            self._set_state(pid, EATING)
            time.sleep(random.uniform(0.5, 1.2) / self.speed)
            self._log(f"P{pid + 1} finished eating")

            self.forks[second].release()
            self.forks[first].release()

    # ------------------------------------------------------------------
    def start(self):
        if self.threads:
            return  # already started
        self._stop_flag.clear()
        self._paused.set()
        for i in range(self.n):
            t = threading.Thread(target=self._philosopher_life, args=(i,), daemon=True)
            self.threads.append(t)
            t.start()

    def pause(self):
        self._paused.clear()

    def resume(self):
        self._paused.set()

    def stop(self):
        self._stop_flag.set()
        self._paused.set()
        self.threads = []


# ---------------------------------------------------------------------------
# Producer-Consumer (alternative synchronization demo, logic only)
# ---------------------------------------------------------------------------
class ProducerConsumer:
    """
    Simple bounded-buffer Producer-Consumer simulation using a semaphore-like
    counter. Provided for completeness; the GUI currently focuses on the
    Dining Philosophers visualization.
    """

    def __init__(self, buffer_size=5, log_callback=None):
        self.buffer_size = buffer_size
        self.buffer = []
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)
        self.log_callback = log_callback
        self._stop_flag = threading.Event()

    def _log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def produce(self, item):
        with self.not_full:
            while len(self.buffer) >= self.buffer_size and not self._stop_flag.is_set():
                self.not_full.wait(timeout=0.5)
            if self._stop_flag.is_set():
                return
            self.buffer.append(item)
            self._log(f"Produced item {item} (buffer={len(self.buffer)}/{self.buffer_size})")
            self.not_empty.notify()

    def consume(self):
        with self.not_empty:
            while not self.buffer and not self._stop_flag.is_set():
                self.not_empty.wait(timeout=0.5)
            if self._stop_flag.is_set():
                return None
            item = self.buffer.pop(0)
            self._log(f"Consumed item {item} (buffer={len(self.buffer)}/{self.buffer_size})")
            self.not_full.notify()
            return item

    def stop(self):
        self._stop_flag.set()
