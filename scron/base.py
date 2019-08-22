# Copyright 2019 Wojciech Banaś
# This code is released under the GPL3 or individual commercial license.

from machine import Timer
from utime import localtime, sleep_ms, time, ticks_ms

from scron.scount import SimpleCounter


class SimpleCRONBase(SimpleCounter):

    def __init__(self, *args, **kwargs):
        super(SimpleCRONBase, self).__init__(*args, **kwargs)
        self.timer = None

    def _sync_time(self):
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
        # Immediate triggering
        # There may also be no negative values of
        if current >= self.time_change:
            out = delta_time_ms - (current - self.time_change)
        else:
            out = delta_time_ms - (1000 - (self.time_change - current))
        if out < 0:
            return 0
        else:
            return out

    def _first_step(self):
        if self.timer == None:
            return
        self.timer.deinit()
        if len(self.callbacks) > 0:
            next_pointer = self.get_next_pointer(*self.get_current_pointer())
            if next_pointer == None:
                # Possible when the callback is removed during operation.
                if len(self.callbacks) > 0:
                    # This situation should not happen. If there is a callback, then the next indicator must exist.
                    raise Exception('scron bug,1')
                return
            self.next_step(*next_pointer)(self.timer)

    def _wait_for_unlock_rw(self):
        """\
        Waiting for the lock to be removed
        """
        # We wait 5 seconds, if the lock is not removed then we emit an error.
        from utime import sleep_ms
        for i in range(5000):
            sleep_ms(1)
            if not self._lock_rw:
                return
        raise Exception('Too long to wait for the lock to be removed!')

    def remove(self, callback_name, force=False, _lock=True):
        """
        Removes from the counters a callback that occurs under ID callback_name.

        Recalculates the nearest callback to call.

        :param force: force removal of the callback.
        :param callback_name: callback name
        """
        super(SimpleCRONBase, self).remove(callback_name, force, _lock)
        self._first_step()

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
        self._sync_time()
