# Copyright 2019 Wojciech Banaś
# This code is released under the GPL3 or individual commercial license.

try:
    from utime import mktime
except:
    # micropython Unix port
    from time import mktime

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
