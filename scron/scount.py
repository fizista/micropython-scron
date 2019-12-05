# Copyright 2019 Wojciech Banaś
# This code is released under the GPL3 or individual commercial license.

from scron.helpers import OrderedDict, CounterDict


class SimpleCounter():
    WILDCARD_VALUE = -1
    _lock_rw = False

    # The dictionary contains a description of all the fields counter.
    # The order is important!!!
    #
    # Examples:
    # OrderedDict([ ('hundreds', 9), ('dozens', 9), ('unity', 9)])
    # OrderedDict([('weekdays', 6), ('hours', 23), ('minutes', 59), ('seconds', 59)])
    #
    # <highest counter pointer> is hundreds or weekdays

    TIME_TABLE_KEYS = OrderedDict()

    # A list of functions that process the captured exception, received from the running callback.
    # processor_exception_function(exception_instance)
    callback_exception_processors = [lambda e: print('Callback EXCEPTION: %s' % e)]

    def __init__(self):
        self.time_table = OrderedDict()
        # callbacks = {<callback_name>: <callback>, ...}
        self.callbacks = {}
        # callbacks_memory = {<callback_name>: {}, ...}
        self.callbacks_memory = {}

    # #####################
    # SCOUNT - START
    def _validate_value(self, input_name, value, max_digit):
        """\
        Validates the value. In the case of errors, throws an exception.

        :param input_name: name input field
        :param value: field value that contains an integer in the range 0-max_digit or WILDCARD_VALUE.
        :param max_digit: the maximum value a field can contain
        :return: int
        """
        try:
            value = int(value)
        except TypeError as e:
            raise ValueError('Bad value in "%s". It can only be an integer, but it is "%s".' % (input_name, value))

        if 0 <= value <= max_digit or value == self.WILDCARD_VALUE:
            return value
        else:
            raise ValueError(
                'Bad value in "%s". It can be a 0-%d or WILDCARD_VALUE number, but it is "%s".' % (
                    input_name,
                    max_digit,
                    value
                )
            )

    def _validate_input(self, input_name, input, max_digit):
        """\
        Validates the field value. In the case of errors, throws an exception.

        :param input_name: name input field
        :param input: field value that contains an integer or list of integers that are in the range 0-max_digit or WILDCARD_VALUE
        :param max_digit: the maximum value a field can contain
        :return: list of integers, or [self.WILDCARD_VALUE]
        """
        try:
            values = []
            if len(input) == 0:
                raise ValueError('An empty list is not allowed.')
            for key, input_value in enumerate(input):
                values.append(
                    self._validate_value(
                        '%s[%d]' % (input_name, key),
                        input_value,
                        max_digit
                    )
                )
            values = list(set(values))
            values.sort()
            if len(values) == (max_digit + 1) or self.WILDCARD_VALUE in values:
                values = [self.WILDCARD_VALUE]
            return values
        except TypeError:
            return [self._validate_value(input_name, input, max_digit)]

    def _get_nearest_time_pointer(self, *current_pointer):
        """
        Returns time pointer + one smallest step.

        :param pointer: index 0 -> highest counter
        :return:
        """
        # We find the nearest possible time after the current one
        nearest_time_pointer = []
        current_time_pointer_reversed = list(reversed(current_pointer))
        current_time_pointer_reversed[0] += 1
        time_max_digits = list(reversed(list(self.TIME_TABLE_KEYS.values())))
        for key, time_max_digit in enumerate(time_max_digits):
            current_value = current_time_pointer_reversed[key]
            if current_value > time_max_digit:
                current_value = 0
                if (key + 1) < len(self.TIME_TABLE_KEYS):
                    current_time_pointer_reversed[key + 1] += 1
            nearest_time_pointer.append(current_value)
        nearest_time_pointer = list(reversed(nearest_time_pointer))
        return nearest_time_pointer

    def _wait_for_unlock_rw(self):
        """\
        Returns the current pointer for the counter.
        """
        raise NotImplementedError()

    # SCOUNT - END
    # #####################

    def add(self, callback_name, callback, *time_steps, removable=True):
        """\
        Adds an entry to the current queue.

        :param callback_name: callback name ID
        :param callback: callable(<SimpleCRON_instance>, <callback_name>, <current_pointer>)
        :param time_steps: list counters steps, eg. [[2,5], 3, 1, [2,3,4]], index 0 -> highest counter
        :param removable: boolean if false, then the entry cannot normally be deleted
        :return: None
        """
        self._wait_for_unlock_rw()

        if not callable(callback):
            raise TypeError("Callback object isn't callable")

        time_steps_validated = []
        for time_step_key, (time_table_key, time_table_value) in enumerate(self.TIME_TABLE_KEYS.items()):
            time_steps_validated.append(
                self._validate_input(
                    time_table_key,
                    time_steps[time_step_key],
                    time_table_value
                )
            )

        max_level = len(self.TIME_TABLE_KEYS)
        # [ (time_table_part, <keys to check>, <current key>) ]
        time_table_parts = [[self.time_table, time_steps_validated[0][:], None]]

        while True:
            level = len(time_table_parts) - 1
            if time_table_parts[-1][2] is None:
                if len(time_table_parts[-1][1]) > 0:
                    current_key = time_table_parts[-1][1].pop()
                    current_key_init = True
                else:
                    del time_table_parts[-1]
                    continue
            else:
                current_key = time_table_parts[-1][2]
                current_key_init = False

            if current_key not in time_table_parts[-1][0]:
                if level < (max_level - 1):
                    time_table_parts[-1][0][current_key] = OrderedDict()
                else:
                    time_table_parts[-1][0][current_key] = set()
                dict_sorted = OrderedDict(sorted(time_table_parts[-1][0].items()))
                time_table_parts[-1][0].clear()
                time_table_parts[-1][0].update(dict_sorted)
                del dict_sorted

            current_value = time_table_parts[-1][0][current_key]

            if current_key_init:
                if type(current_value) is set:
                    current_value.add(callback_name)

                    if len(time_table_parts[-1][1]) > 0:
                        time_table_parts[-1][2] = None
                    else:
                        del time_table_parts[-1]
                else:
                    time_table_parts[-1][2] = current_key
                    time_table_parts.append([current_value, time_steps_validated[level + 1][:], None])

            else:
                if len(time_table_parts[-1][1]) > 0:
                    time_table_parts[-1][2] = None
                else:
                    if len(time_table_parts) == 1:
                        break
                    else:
                        del time_table_parts[-1]

        self.callbacks[callback_name] = (callback, removable)
        self.callbacks_memory[callback_name] = {}

    def callback_exists(self, callback_name):
        """\
        Checking if a callback exists

        :param callback_name:
        :return: boolean
        """
        return callback_name in self.callbacks

    def get_current_pointer(self):
        """\
        Returns the current pointer for the counter.

        It must contain the same number of entries as is defined in TIME_TABLE_KEYS.

        :return: tuple(<highest counter pointer>, ...)
        """
        raise NotImplementedError()

    def get_next_pointer(self, *current_pointer):
        """\
        Returns the nearest next pointer for the counter.

        :param current_pointer: index 0 -> highest counter

        :return: tuple(<highest counter pointer>, ...) or None
        """
        if len(self.callbacks) == 0:
            return None

        self._wait_for_unlock_rw()

        # We find the nearest possible time after the current one
        next_time_pointer = self._get_nearest_time_pointer(*current_pointer)

        def get_first(time_table_node_base):

            max_level = len(self.TIME_TABLE_KEYS)
            time_table_node = time_table_node_base
            out_value = tuple()
            for level in range(max_level + 1):
                if type(time_table_node) == set:
                    break
                key, time_table_node = next(iter(time_table_node.items()))
                out_value += (key,)
            return out_value

        time_max_digits = list(self.TIME_TABLE_KEYS.values())
        time_table_base = CounterDict(self.time_table, time_max_digits)

        max_level = len(self.TIME_TABLE_KEYS)
        time_table_node = time_table_base
        time_table_parts = [time_table_base]
        out_value = tuple()
        level = 0
        while True:
            current_value = next_time_pointer[level]
            for next_value, time_table_value in time_table_node.items():
                if next_value > current_value:
                    out_value += (next_value,) + get_first(time_table_value)
                    return out_value
                elif next_value == current_value:
                    out_value += (next_value,)
                    time_table_node = time_table_value
                    time_table_parts.append(time_table_value)
                    level += 1
                    break
                else:
                    continue
            else:
                if (level - 1) == -1:
                    return get_first(time_table_base)
                if next_time_pointer[level - 1] == list(self.TIME_TABLE_KEYS.values())[level - 1]:
                    next_time_pointer[level - 1] = 0
                else:
                    next_time_pointer[level - 1] = next_time_pointer[level - 1] + 1
                next_time_pointer[level:] = [0] * len(next_time_pointer[level:])
                out_value = out_value[:-1]
                level -= 1
                time_table_node = time_table_parts[level]
                del time_table_parts[level:]

            if len(out_value) == max_level:
                return out_value

        raise Exception('???')

    def list(self, _time_table_node=None, _prev_data=None):
        """\
        Returns the generator containing full and ordered information about all steps.

        :param _time_table_node: internal variable
        :param _prev_data: internal variable
        :return:
        """
        self._wait_for_unlock_rw()

        if type(_time_table_node) is set:
            yield _prev_data + (_time_table_node,)
        else:
            if _prev_data == None:
                _prev_data = tuple()

            if _time_table_node == None:
                _time_table_node = self.time_table

            for time_table_key, time_table_value in _time_table_node.items():
                yield from self.list(time_table_value, _prev_data + (time_table_key,))

    def remove_all(self, force=False):
        """\
        Removes all calls from the counters.

        :param force: force removal of the callback.
        :return:
        """
        to_remove = []
        for callback_name, data in self.callbacks.items():
            # We're checking to see if we can remove it.
            if force or data[1]:
                to_remove.append(callback_name)
        for callback_name in to_remove:
            self.remove(callback_name, force)

    def remove(self, callback_name, force=False, _lock=True):
        """\
        Removes from the counters a callback that occurs under ID callback_name.

        :param callback_name: callback name ID
        :param force: force removal of the callback.
        :return:
        """
        if callback_name not in self.callbacks:
            return

        # Imposing a blockade of changes on the callback database.
        self._lock_rw = _lock

        if not force:
            if not self.callbacks[callback_name][1]:
                raise Exception('This callback cannot be removed!')

        max_level = len(self.TIME_TABLE_KEYS)
        # [ (time_table_part, <keys to check>, <current key>) ]
        time_table_parts = [[self.time_table, list(self.time_table.keys()), None]]
        while len(time_table_parts) > 0:
            if time_table_parts[-1][2] is None:
                if len(time_table_parts[-1][1]) > 0:
                    current_key = time_table_parts[-1][1].pop()
                    current_key_init = True
                else:
                    del time_table_parts[-1]
                    continue
            else:
                current_key = time_table_parts[-1][2]
                current_key_init = False

            current_value = time_table_parts[-1][0][current_key]

            if current_key_init:
                if type(current_value) is set:
                    if callback_name in current_value:
                        current_value.remove(callback_name)
                        if len(current_value) == 0:
                            del time_table_parts[-1][0][current_key]
                    if len(time_table_parts[-1][1]) > 0:
                        time_table_parts[-1][2] = None
                    else:
                        del time_table_parts[-1]
                else:
                    time_table_parts[-1][2] = current_key
                    time_table_parts.append([current_value, list(current_value.keys()), None])

            else:
                if len(current_value) == 0:
                    del time_table_parts[-1][0][current_key]
                if len(time_table_parts[-1][1]) > 0:
                    time_table_parts[-1][2] = None
                else:
                    del time_table_parts[-1]

        self.callbacks.pop(callback_name)
        self.callbacks_memory.pop(callback_name)

        # Removal of the blockade of changes in the callback database.
        self._lock_rw = False

    def run_callbacks(self, *global_current_pointer):
        """\
        Runs all callbacks for a given pointer.

        :param current_pointer: index 0 -> highest counter
        :return:
        """
        self._wait_for_unlock_rw()

        get_exactly_stack = [(self.time_table, global_current_pointer)]

        while get_exactly_stack:
            time_table_node, current_pointer = get_exactly_stack.pop()
            if type(time_table_node) == set:
                for callback_name in time_table_node:
                    try:
                        self.callbacks[callback_name][0](
                            self,
                            callback_name,
                            global_current_pointer,
                            self.callbacks_memory[callback_name]
                        )
                    except Exception as e:
                        for processor in self.callback_exception_processors:
                            processor(e)
            else:
                if self.WILDCARD_VALUE in time_table_node:
                    get_exactly_stack.append((time_table_node[self.WILDCARD_VALUE], current_pointer[1:]))
                if current_pointer[0] in time_table_node:
                    get_exactly_stack.append((time_table_node[current_pointer[0]], current_pointer[1:]))
