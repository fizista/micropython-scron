# Copyright 2019 Wojciech Banaś
# This code is released under the GPL3 or individual commercial license.

try:
    from collections import OrderedDict


    def assert_dict(dict_a, dict_b):
        assert list(dict_a.items()) == list(dict_b.items())


    def repr_dict(dictionary):
        out_values = []
        for key, value in dictionary.items():
            out_values.append('(%s, %s)' % (key, value))
        return '%s([%s])' % (dictionary.__class__.__name__, ', '.join(out_values))

except ImportError:
    from ucollections import OrderedDict


    # micropython has problems with comparing dictionaries, so here is a workaround
    def assert_dict(dict_a, dict_b):
        def normalize(d):
            return \
                d.replace(dict_a.__class__.__name__, 'OrderedDict'). \
                    replace(dict_b.__class__.__name__, 'OrderedDict'). \
                    replace(' ', '')

        norm_a = normalize(str(dict_a))
        norm_b = normalize(str(dict_b))
        assert norm_a == norm_b


    def repr_dict(dictionary):
        out_values = []
        for key, value in dictionary.items():
            out_values.append('%s: %s' % (key, value))
        return '%s({%s})' % (dictionary.__class__.__name__, ', '.join(out_values))


def merge_tree(tree_a, tree_b):
    """\
    It connects two OrderDict trees into one.

    Both trees must have the same number of branches. At the end of the branch, there must be an object of "set".

    :param tree_a: OrderDict
    :param tree_b: OrderDict
    :return: OrderDict_A + OrderDict_B
    """
    if type(tree_a) is set and type(tree_b) is set:
        return tree_a.union(tree_b)

    keys = list(set(tuple(tree_a.keys()) + tuple(tree_b.keys())))
    keys.sort()

    out = OrderedDict()

    for key in keys:
        if key in tree_a and key in tree_b:
            out[key] = merge_tree(tree_a[key], tree_b[key])
        elif key in tree_a:
            out[key] = tree_a[key]
        elif key in tree_b:
            out[key] = tree_b[key]
    return out


class CounterDict:
    WILDCARD_VALUE = -1

    def __init__(self, count_table, count_table_limits):
        """\
        Tree decorator. Expands the input tree "count_table" into the expected structure/tree.

        len(count_table_limits) == nesting level "count_table".

        Example:
        count_table_limits = [2,4]
        count_table = OrderDict([
            (1, OrderDict([
                    (3, set('1_3'))
                ])
            ),
            (2, OrderDict([
                    (0, set('2_0'))
                    (4, set('2_4'))
                ])
            )
        ])

        count_table.keys() <= count_table_limits[0]
        count_table[x].keys() <= count_table_limits[1]

        :param count_table: OrderDict
        :param count_table_limits: list
        """
        self.count_table = count_table
        self.count_table_limits = count_table_limits
        if len(list(self.keys())) > 0:
            if max(self.keys()) > count_table_limits[0]:
                raise KeyError('Keys can have a maximum value of %d' % count_table_limits[0])

    def items(self):
        def get_value(key, value):
            if type(value) is OrderedDict:
                yield key, CounterDict(value, self.count_table_limits[1:])
            else:
                yield key, value

        if self.WILDCARD_VALUE in self.count_table:
            for key in range(0, self.count_table_limits[0] + 1):
                if key in self.count_table:
                    value_combined = merge_tree(self.count_table[key], self.count_table[self.WILDCARD_VALUE])
                    yield from get_value(key, value_combined)
                else:
                    yield from get_value(key, self.count_table[self.WILDCARD_VALUE])
        else:
            for key, value in self.count_table.items():
                yield from get_value(key, value)

    def keys(self):
        if self.WILDCARD_VALUE in self.count_table:
            return range(0, self.count_table_limits[0] + 1)
        else:
            return self.count_table.keys()

    def values(self):
        def get_value(value):
            if type(value) is OrderedDict:
                yield CounterDict(value, self.count_table_limits[1:])
            else:
                yield value

        if self.WILDCARD_VALUE in self.count_table:
            for key in range(0, self.count_table_limits[0] + 1):
                if key in self.count_table:
                    value_combined = merge_tree(self.count_table[key], self.count_table[self.WILDCARD_VALUE])
                    yield from get_value(value_combined)
                else:
                    yield from get_value(self.count_table[self.WILDCARD_VALUE])
        else:
            for key, value in self.count_table.items():
                yield from get_value(value)

    def __delattr__(self, item):
        pass

    def __eq__(self, other):
        if type(other) not in (OrderedDict, CounterDict):
            return False
        try:
            assert_dict(other, self)
        except AssertionError as e:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return repr_dict(self)


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

    def __init__(self):
        self.time_table = OrderedDict()
        # callbacks = {<callback_name>: <callback>, ...}
        self.callbacks = {}
        # callbacks_memory = {<callback_name>: {}, ...}
        self.callbacks_memory = {}

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

        time_steps_validated = []
        for time_step_key, (time_table_key, time_table_value) in enumerate(self.TIME_TABLE_KEYS.items()):
            time_steps_validated.append(
                self._validate_input(
                    time_table_key,
                    time_steps[time_step_key],
                    time_table_value
                )
            )

        def insert_part(time_table_node, level=0):
            if level == len(time_steps_validated):
                time_table_node.add(callback_name)
                return time_table_node

            for time_step_validated in time_steps_validated[level]:
                if time_step_validated not in time_table_node:
                    if level == (len(time_steps_validated) - 1):
                        time_table_node[time_step_validated] = set()
                    else:
                        time_table_node[time_step_validated] = OrderedDict()

                time_table_node[time_step_validated] = insert_part(time_table_node[time_step_validated], level + 1)

            return OrderedDict(sorted(time_table_node.items()))

        self.time_table = insert_part(self.time_table)

        self.callbacks[callback_name] = (callback, removable)
        self.callbacks_memory[callback_name] = {}

    def callback_exists(self, callback_name):
        """\
        Checking if a callback exists

        :param callback_name:
        :return: boolean
        """
        return callback_name in self.callbacks

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

    def get_current_pointer(self):
        """\
        Returns the current pointer for the counter.

        It must contain the same number of entries as is defined in TIME_TABLE_KEYS.

        :return: tuple(<highest counter pointer>, ...)
        """
        raise NotImplementedError()

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
                    self.callbacks[callback_name][0](
                        self,
                        callback_name,
                        global_current_pointer,
                        self.callbacks_memory[callback_name]
                    )
            else:
                if self.WILDCARD_VALUE in time_table_node:
                    get_exactly_stack.append((time_table_node[self.WILDCARD_VALUE], current_pointer[1:]))
                if current_pointer[0] in time_table_node:
                    get_exactly_stack.append((time_table_node[current_pointer[0]], current_pointer[1:]))

    def _wait_for_unlock_rw(self):
        """\
        Returns the current pointer for the counter.
        """
        raise NotImplementedError()
