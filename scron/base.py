# Copyright 2019 Wojciech Banaś
# This code is released under the GPL3 or individual commercial license.

from machine import Timer
from utime import localtime, sleep_ms, time, ticks_ms

try:
    from utime import mktime
except:
    # micropython Unix port
    from time import mktime

try:
    from collections import OrderedDict
except ImportError:
    from ucollections import OrderedDict

from scron.scount import SimpleCounter

WILDCARD = SimpleCounter.WILDCARD_VALUE


class SimpleCRONBase(SimpleCounter):

    def __init__(self, *args, **kwargs):
        super(SimpleCRONBase, self).__init__(*args, **kwargs)
        self.timer = None

    def add(self, callback_name, callback, *time_steps):
        super(SimpleCRONBase, self).add(callback_name, callback, *time_steps)
        self._first_step()

    def sync_time(self):
        "Synchronizes SimpleCRON with time."
        self.set_time_change(self.estimate_time_change())
        self._first_step()

    def estimate_time_change(self):
        """\
        Estimate the time change.
        :return:
        """
        last = int(time()) + 1
        current = last
        while 1:
            current = int(time())
            if current > last:
                return (self.get_time_change_pointer() + 1) % 1000
            sleep_ms(1)

    def set_time_change(self, time_change):
        self.time_change = time_change

    def get_time_change_pointer(self):
        return ticks_ms()

    def get_time_change_correction(self, delta_time_ms):
        current = self.get_time_change_pointer() % 1000
        if current >= self.time_change:
            return delta_time_ms - (current - self.time_change)
        else:
            return delta_time_ms - (1000 - (self.time_change - current))

    def run(self, timer_id=1):
        # One good start up is enough
        if self.timer is not None:
            raise Exception('You can run SimpleCRON once.')
        timer = Timer(timer_id)
        # Check if this timer is possible to use
        # If not, we will get an error: OSError: 261
        timer.init(period=1, mode=Timer.ONE_SHOT, callback=lambda t: None)
        self.timer = timer
        self.sync_time()

    def _first_step(self):
        if self.timer == None:
            return
        self.timer.deinit()
        self.next_step(*self.get_next_pointer(*self.get_current_pointer()))(self.timer)

    def remove(self, callback_name):
        super(SimpleCRONBase, self).remove(callback_name)
        self._first_step()

    def remove_all(self):
        super(SimpleCRONBase, self).remove_all()
        self._first_step()
