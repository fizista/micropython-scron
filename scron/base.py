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
        self._set_time_change(self._estimate_time_change())
        self._first_step()

    def _estimate_time_change(self):
        """\
        Estimate the time change.
        :return:
        """
        last = int(time()) + 1
        current = last
        while 1:
            current = int(time())
            if current > last:
                return (self._get_time_change_pointer() + 1) % 1000
            sleep_ms(1)

    def _set_time_change(self, time_change):
        self.time_change = time_change

    def _get_time_change_pointer(self):
        return ticks_ms()

    def _get_time_change_correction(self, delta_time_ms):
        current = self._get_time_change_pointer() % 1000
        if current >= self.time_change:
            return delta_time_ms - (current - self.time_change)
        else:
            return delta_time_ms - (1000 - (self.time_change - current))

    def run(self, timer_id=1):
        """
        Initiates a list of tasks and reserves one hardware timer.

        **Warning:**
        "OSError: 261" - error means a problem with the hardware timer.
        Try to set another timer ID.
        `See MicroPython documentation for machine.Timer. <https://docs.micropython.org/en/latest/library/machine.Timer.html>`_

        :param timer_id: hardware timer ID
        """
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
        if len(self.callbacks.keys()) > 0:
            self.next_step(*self.get_next_pointer(*self.get_current_pointer()))(self.timer)

    def remove(self, callback_name):
        """
        Removes from the counters a callback that occurs under ID callback_name.

        Recalculates the nearest callback to call.

        :param callback_name: callback name
        """
        super(SimpleCRONBase, self).remove(callback_name)
        self._first_step()

    def remove_all(self):
        """\
        Removes all calls from the counters.

        Stops the countdown to the nearest callback.
        """
        super(SimpleCRONBase, self).remove_all()
        self._first_step()
