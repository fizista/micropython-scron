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

from scron.base import SimpleCRONBase

WILDCARD = SimpleCRONBase.WILDCARD_VALUE


class SimpleCRON(SimpleCRONBase):
    TIME_TABLE_KEYS = OrderedDict([('weekdays', 6), ('hours', 23), ('minutes', 59), ('seconds', 59)])

    def add(self, callback_name, callback, seconds=WILDCARD, minutes=WILDCARD, hours=WILDCARD, weekdays=WILDCARD):
        """\
        Adds an entry to the current queue.

        After adding a callback, the next call is recalculated.

        :param callback_name: callback name ID
        :param callback: callable
        :param seconds: 0-59 or list(second, ...), default: SimpleCRON.WILDCARD_VALUE
        :param minutes: 0-59 or list(minutes, ...), default: SimpleCRON.WILDCARD_VALUE
        :param hours: 0-23 or list(hours, ...), default: SimpleCRON.WILDCARD_VALUE
        :param weekdays: 0-6 or list(days, ...) 0=monday,6=sunday, default: SimpleCRON.WILDCARD_VALUE
        :return: None
        """
        super(SimpleCRON, self).add(callback_name, callback, weekdays, hours, minutes, seconds)

    def get_current_pointer(self):
        """
        Returns the pointer generated from the current date.

        :return: tuple(weekday, hour, minute, second)
        """
        year, month, mday, hour, minute, second, weekday, yearday = localtime()
        return weekday, hour, minute, second

    def get_next_pointer(self, weekday, hour, minute, second):
        """
        Returns the nearest next pointer for the counter.

        :param weekday: 0-6, 0=monday,6=sunday
        :param hour: 0-23
        :param minute: 0-59
        :param second: 0-59
        :return: tuple(weekday, hour, minute, second)
        """
        return super(SimpleCRON, self).get_next_pointer(weekday, hour, minute, second)

    def run_callbacks(self, weekday, hour, minute, second):
        """
        Runs all callbacks for a given pointer.

        :param weekday: 0-6, 0=monday,6=sunday
        :param hour: 0-23
        :param minute: 0-59
        :param second: 0-59
        """
        return super(SimpleCRON, self).run_callbacks(weekday, hour, minute, second)

    def next_step(self, *last_time_pointer):
        """
        Returns the generated function for the timer.

        :param last_time_pointer: last call pointer
        :return: function(timer_instance)
        """

        def _next_step(timer):
            current_pointer = self.get_current_pointer()
            next_time_pointer = self.get_next_pointer(*current_pointer)

            def is_the_same_callback():
                # Skip callbacks calls when time does not match.
                if next_time_pointer == last_time_pointer:
                    if current_pointer == next_time_pointer:
                        return False
                    return True
                return False

            # There are no new tasks in the future, so we finish
            if next_time_pointer == None:
                if not is_the_same_callback():
                    self.run_callbacks(*last_time_pointer)
                return

            # zero day
            def get_zero_day_time_sec(year, month, mday, hour, minute, second, weekday, yearday):
                return mktime(current) - weekday * 24 * 60 * 60 - hour * 60 * 60 - minute * 60 - second

            def get_pointer_sec(weekday, hour, minute, second):
                return weekday * 24 * 60 * 60 + hour * 60 * 60 + minute * 60 + second

            current = localtime()
            zero_day_time_sec = get_zero_day_time_sec(*current)

            period_seconds = zero_day_time_sec + get_pointer_sec(*next_time_pointer) - mktime(current)
            period_mili_seconds = self._get_time_change_correction(period_seconds * 1000)

            timer.init(
                period=period_mili_seconds,
                mode=Timer.ONE_SHOT,
                callback=self.next_step(*next_time_pointer)
            )

            if not is_the_same_callback():
                self.run_callbacks(*last_time_pointer)

        return _next_step


simple_cron = SimpleCRON()
