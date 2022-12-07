# -*- coding: utf-8 -*-

import typing as T
import time
import itertools


class Waiter:
    """
    Simple retry / poll.
    """
    def __init__(self, delays: T.Union[int, float], timeout: T.Union[int, float]):
        self.delays = itertools.repeat(delays)
        self.timeout = timeout

    def __iter__(self):
        start = time.time()
        end = start + self.timeout
        for attempt, delay in enumerate(self.delays, 1):
            now = time.time()
            remaining = end - now
            if remaining < 0:
                raise TimeoutError(f"timed out in {self.timeout} seconds!")
            else:
                time.sleep(min(delay, remaining))
                elapsed = now - start + delay
                yield attempt, round(elapsed, 2)
