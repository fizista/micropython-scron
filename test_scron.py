import unittest
from scron.week import SimpleCRON
from scron.scount import CounterDict, merge_tree
from scron.decorators import run_times, call_counter, time_since_last_call

try:
    from collections import OrderedDict
except ImportError:
    from ucollections import OrderedDict


class TestFunctions(unittest.TestCase):

    def test_merge_tree(self):
        tree_a = OrderedDict([
            (-1, OrderedDict([(1, {'-1_1'}), (2, {'-1_2'})])),
            (1, OrderedDict([(1, {'1_1'}), (2, {'1_2'})])),
            (2, OrderedDict([(1, {'2_1'}), (2, {'2_2'})])),
        ])
        tree_b1 = OrderedDict([
            (-1, OrderedDict([(-1, {'-1_-1'}), (2, {'-1_2'})])),
        ])
        self.assertEqual(
            merge_tree(tree_a, tree_b1),
            OrderedDict([
                (-1, OrderedDict([(-1, {'-1_-1'}), (1, {'-1_1'}), (2, {'-1_2'})])),
                (1, OrderedDict([(1, {'1_1'}), (2, {'1_2'})])),
                (2, OrderedDict([(1, {'2_1'}), (2, {'2_2'})])),
            ])
        )

        tree_b2 = OrderedDict([
            (-1, OrderedDict([(1, {'-1_1'}), (2, {'-1_2'})])),
            (1, OrderedDict([(1, {'1_1'}), (2, {'1_2'})])),
            (2, OrderedDict([(1, {'2_1'}), (2, {'2_2'})])),
        ])
        self.assertEqual(
            merge_tree(tree_a, tree_b2),
            OrderedDict([
                (-1, OrderedDict([(1, {'-1_1'}), (2, {'-1_2'})])),
                (1, OrderedDict([(1, {'1_1'}), (2, {'1_2'})])),
                (2, OrderedDict([(1, {'2_1'}), (2, {'2_2'})])),
            ])
        )

        tree_b3 = OrderedDict([
            (3, OrderedDict([(1, {'2_1'}), (2, {'2_2'})])),
        ])
        self.assertEqual(
            merge_tree(tree_a, tree_b3),
            OrderedDict([
                (-1, OrderedDict([(1, {'-1_1'}), (2, {'-1_2'})])),
                (1, OrderedDict([(1, {'1_1'}), (2, {'1_2'})])),
                (2, OrderedDict([(1, {'2_1'}), (2, {'2_2'})])),
                (3, OrderedDict([(1, {'2_1'}), (2, {'2_2'})])),
            ])
        )


class TestTimeTableNormalDict(unittest.TestCase):

    def setUp(self):
        self.count_table = OrderedDict([
            (2, OrderedDict([(4, {'2_4'}), (5, {'2_5'})])),
            (5, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),
            (8, OrderedDict([(2, {'8_2'}), (5, {'8_5'})])),
        ])
        self.count_table_limits = [8, 5]

    def test_equal(self):
        self.assertTrue(
            CounterDict(self.count_table, self.count_table_limits) == self.count_table,
            msg="%r \n %r" % (CounterDict(self.count_table, self.count_table_limits), self.count_table)
        )

    def test_keys(self):
        self.assertEqual(
            list(CounterDict(self.count_table, self.count_table_limits).keys()),
            [2, 5, 8]
        )

    def test_values(self):
        self.assertEqual(
            list(CounterDict(self.count_table, self.count_table_limits).values()),
            [
                OrderedDict([(4, {'2_4'}), (5, {'2_5'})]),
                OrderedDict([(4, {'5_4'}), (5, {'5_5'})]),
                OrderedDict([(2, {'8_2'}), (5, {'8_5'})]),
            ]
        )

    def test_items(self):
        self.assertEqual(
            list(CounterDict(self.count_table, self.count_table_limits).items()),
            [
                (2, OrderedDict([(4, {'2_4'}), (5, {'2_5'})])),
                (5, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),
                (8, OrderedDict([(2, {'8_2'}), (5, {'8_5'})])),
            ]
        )


class TestTimeTableWildcardDict(unittest.TestCase):

    def setUp(self):
        self.count_table = OrderedDict([
            (2, OrderedDict([(4, {'2_4'}), (5, {'2_5'})])),
            (CounterDict.WILDCARD_VALUE, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),
            (8, OrderedDict([(2, {'8_2'}), (5, {'8_5'})])),
        ])
        self.count_table_limits = [8, 5]

    def test_equal(self):
        self.assertTrue(CounterDict(self.count_table, self.count_table_limits) != self.count_table)
        correct_dict = OrderedDict([
            (0, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),
            (1, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),

            (2, OrderedDict([(4, {'2_4', '5_4'}), (5, {'2_5', '5_5'})])),  #

            (3, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),
            (4, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),

            (5, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),

            (6, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),
            (7, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),

            (8, OrderedDict([(2, {'8_2'}), (4, {'5_4'}), (5, {'5_5', '8_5'})])),  #
        ])
        self.assertTrue(CounterDict(self.count_table, self.count_table_limits) == correct_dict)

    def test_keys(self):
        self.assertEqual(
            list(CounterDict(self.count_table, self.count_table_limits).keys()),
            [0, 1, 2, 3, 4, 5, 6, 7, 8]
        )

    def test_values(self):
        self.assertEqual(
            list(CounterDict(self.count_table, self.count_table_limits).values()),
            [
                OrderedDict([(4, {'5_4'}), (5, {'5_5'})]),
                OrderedDict([(4, {'5_4'}), (5, {'5_5'})]),

                OrderedDict([(4, {'2_4', '5_4'}), (5, {'2_5', '5_5'})]),  #

                OrderedDict([(4, {'5_4'}), (5, {'5_5'})]),
                OrderedDict([(4, {'5_4'}), (5, {'5_5'})]),

                OrderedDict([(4, {'5_4'}), (5, {'5_5'})]),

                OrderedDict([(4, {'5_4'}), (5, {'5_5'})]),
                OrderedDict([(4, {'5_4'}), (5, {'5_5'})]),

                OrderedDict([(2, {'8_2'}), (4, {'5_4'}), (5, {'5_5', '8_5'})]),  #
            ]
        )

    def test_items(self):
        self.assertEqual(
            list(CounterDict(self.count_table, self.count_table_limits).items()),
            [
                (0, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),
                (1, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),

                (2, OrderedDict([(4, {'2_4', '5_4'}), (5, {'2_5', '5_5'})])),  #

                (3, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),
                (4, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),

                (5, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),

                (6, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),
                (7, OrderedDict([(4, {'5_4'}), (5, {'5_5'})])),

                (8, OrderedDict([(2, {'8_2'}), (4, {'5_4'}), (5, {'5_5', '8_5'})])),  #
            ]
        )


class TestSimpleCRON(unittest.TestCase):

    def setUp(self):
        self.simple_cron = SimpleCRON()

    def test_validate_value(self):
        # Test min value
        self.assertEqual(self.simple_cron._validate_value('fieldA', 0, 10), 0)
        # Test max value
        self.assertEqual(self.simple_cron._validate_value('fieldA', 10, 10), 10)
        # Testing a defined value
        self.assertEqual(self.simple_cron._validate_value('fieldA', self.simple_cron.WILDCARD_VALUE, 10),
                         self.simple_cron.WILDCARD_VALUE)

        # Testing values out of range
        with self.assertRaises(ValueError):
            self.simple_cron._validate_value('fieldA', 11, 10)
        with self.assertRaises(ValueError):
            self.simple_cron._validate_value('fieldA', -10, 10)

    def test_validate_input(self):
        # Test min value
        self.assertEqual(self.simple_cron._validate_input('fieldA', 0, 10), [0])
        # Test max value
        self.assertEqual(self.simple_cron._validate_input('fieldA', 10, 10), [10])
        # Test bad values
        with self.assertRaises(ValueError):
            self.simple_cron._validate_input('fieldA', 11, 10)
        with self.assertRaises(ValueError):
            self.simple_cron._validate_input('fieldA', -11, 10)
        # Test range
        self.assertEqual(
            self.simple_cron._validate_input('fieldA', range(0, 11, 2), 10),
            [0, 2, 4, 6, 8, 10]
        )
        # Testing a defined value
        self.assertEqual(
            self.simple_cron._validate_input('fieldA', self.simple_cron.WILDCARD_VALUE, 10),
            [self.simple_cron.WILDCARD_VALUE]
        )
        # Testing WILDCARD_VALUE detection
        self.assertEqual(
            self.simple_cron._validate_input('fieldA', [0, 4, 2, 3, 1], 4),
            [self.simple_cron.WILDCARD_VALUE]
        )
        self.assertEqual(
            self.simple_cron._validate_input('fieldA', [0, self.simple_cron.WILDCARD_VALUE, 4], 4),
            [self.simple_cron.WILDCARD_VALUE]
        )
        # Testing values out of range
        with self.assertRaises(ValueError):
            self.simple_cron._validate_input('fieldA', [], 10)

    def test_add_and_remove_list(self):
        self.simple_cron.add(callback_name='aaa', callback='AAA', seconds=1, minutes=2, hours=3, weekdays=4)
        self.assertEqual(self.simple_cron.callbacks, {'aaa': 'AAA'})
        self.assertEqual(self.simple_cron.callbacks_memory, {'aaa': {}})
        self.assertEqual(
            list(self.simple_cron.list()),
            [
                (4, 3, 2, 1, {'aaa'}),
            ]
        )

        self.simple_cron.add(callback_name='bbb', callback='BBB', seconds=59, minutes=59, hours=23, weekdays=6)
        self.assertEqual(self.simple_cron.callbacks, {'aaa': 'AAA', 'bbb': 'BBB'})
        self.assertEqual(
            list(self.simple_cron.list()),
            [
                (4, 3, 2, 1, {'aaa'}),
                (6, 23, 59, 59, {'bbb'})
            ]
        )

        self.simple_cron.add(callback_name='ccc', callback='CCC', seconds=1, minutes=2, hours=3, weekdays=6)
        self.assertEqual(self.simple_cron.callbacks, {'aaa': 'AAA', 'bbb': 'BBB', 'ccc': 'CCC'})
        self.assertEqual(
            list(self.simple_cron.list()),
            [
                (4, 3, 2, 1, {'aaa'}),
                (6, 3, 2, 1, {'ccc'}),
                (6, 23, 59, 59, {'bbb'})
            ]
        )

        self.simple_cron.remove(callback_name='ccc')
        self.assertEqual(self.simple_cron.callbacks, {'aaa': 'AAA', 'bbb': 'BBB'})
        self.assertEqual(
            list(self.simple_cron.list()),
            [
                (4, 3, 2, 1, {'aaa'}),
                (6, 23, 59, 59, {'bbb'})
            ]
        )

        self.simple_cron.remove(callback_name='bbb')
        self.assertEqual(self.simple_cron.callbacks, {'aaa': 'AAA'})
        self.assertEqual(
            list(self.simple_cron.list()),
            [
                (4, 3, 2, 1, {'aaa'}),
            ]
        )

        self.simple_cron.remove(callback_name='aaa')
        self.assertEqual(self.simple_cron.callbacks, {})
        self.assertEqual(self.simple_cron.time_table, {})
        self.assertEqual(self.simple_cron.callbacks_memory, {})

        self.simple_cron.add(callback_name='aaa', callback='AAA', seconds=1, minutes=2, hours=3,
                             weekdays=range(0, 7, 2))
        self.assertEqual(self.simple_cron.callbacks, {'aaa': 'AAA'})
        self.assertEqual(
            list(self.simple_cron.list()),
            [
                (0, 3, 2, 1, {'aaa'}),
                (2, 3, 2, 1, {'aaa'}),
                (4, 3, 2, 1, {'aaa'}),
                (6, 3, 2, 1, {'aaa'}),
            ]
        )

        self.simple_cron.remove_all()

        self.simple_cron.add(callback_name='1', callback='1', seconds=2, minutes=2, hours=3, weekdays=6)
        self.simple_cron.add(callback_name='2', callback='1', seconds=1, minutes=2, hours=3, weekdays=6)  #

        self.simple_cron.add(callback_name='3', callback='1', seconds=1, minutes=3, hours=3, weekdays=6)
        self.simple_cron.add(callback_name='4', callback='1', seconds=1, minutes=1, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='5', callback='1', seconds=1, minutes=2, hours=3, weekdays=6)  #

        self.simple_cron.add(callback_name='6', callback='1', seconds=1, minutes=2, hours=1, weekdays=6)  #
        self.simple_cron.add(callback_name='7', callback='1', seconds=1, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='8', callback='1', seconds=1, minutes=2, hours=2, weekdays=6)  #

        self.simple_cron.add(callback_name='9', callback='1', seconds=1, minutes=2, hours=2, weekdays=2)  #
        self.simple_cron.add(callback_name='10', callback='1', seconds=1, minutes=2, hours=2, weekdays=1)  #
        self.simple_cron.add(callback_name='11', callback='1', seconds=1, minutes=2, hours=2, weekdays=6)  #

        out = list(self.simple_cron.list())
        self.assertEqual(out[0], (1, 2, 2, 1, {'10'}))
        self.assertEqual(out[1], (2, 2, 2, 1, {'9'}))
        self.assertEqual(out[2], (6, 1, 2, 1, {'6'}))
        self.assertEqual(out[3], (6, 2, 2, 1, {'8', '11'}))
        self.assertEqual(out[4], (6, 3, 1, 1, {'4'}))
        self.assertEqual(out[5], (6, 3, 2, 1, {'7', '2', '5'}))
        self.assertEqual(out[6], (6, 3, 2, 2, {'1'}))
        self.assertEqual(out[7], (6, 3, 3, 1, {'3'}))

        self.simple_cron.remove_all()
        self.assertEqual(
            list(self.simple_cron.list()),
            []
        )

    def test_add_and_remove_list__wildcard(self):
        self.simple_cron.add(callback_name='aaaw', callback='AAAW',
                             seconds=1, minutes=2, hours=3, weekdays=SimpleCRON.WILDCARD_VALUE)
        self.simple_cron.add(callback_name='bbbw', callback='BBBW',
                             seconds=59, minutes=SimpleCRON.WILDCARD_VALUE, hours=23, weekdays=6)
        self.simple_cron.add(callback_name='cccw', callback='CCCW',
                             seconds=1, minutes=2, hours=SimpleCRON.WILDCARD_VALUE, weekdays=6)

        self.simple_cron.add(callback_name='aaa', callback='AAA', seconds=1, minutes=2, hours=3, weekdays=4)
        self.simple_cron.add(callback_name='bbb', callback='BBB', seconds=59, minutes=59, hours=23, weekdays=6)
        self.simple_cron.add(callback_name='ccc', callback='CCC', seconds=1, minutes=2, hours=3, weekdays=6)

        self.assertEqual(self.simple_cron.callbacks, {'aaa': 'AAA', 'bbb': 'BBB', 'ccc': 'CCC',
                                                      'aaaw': 'AAAW', 'bbbw': 'BBBW', 'cccw': 'CCCW'})
        self.assertEqual(
            list(self.simple_cron.list()),
            [
                (SimpleCRON.WILDCARD_VALUE, 3, 2, 1, {'aaaw'}),
                (4, 3, 2, 1, {'aaa'}),
                (6, SimpleCRON.WILDCARD_VALUE, 2, 1, {'cccw'}),
                (6, 3, 2, 1, {'ccc'}),
                (6, 23, SimpleCRON.WILDCARD_VALUE, 59, {'bbbw'}),
                (6, 23, 59, 59, {'bbb'})
            ]
        )

        self.simple_cron.remove(callback_name='cccw')
        self.assertEqual(self.simple_cron.callbacks, {'aaa': 'AAA', 'bbb': 'BBB', 'ccc': 'CCC',
                                                      'aaaw': 'AAAW', 'bbbw': 'BBBW'})
        self.assertEqual(
            list(self.simple_cron.list()),
            [
                (SimpleCRON.WILDCARD_VALUE, 3, 2, 1, {'aaaw'}),
                (4, 3, 2, 1, {'aaa'}),
                (6, 3, 2, 1, {'ccc'}),
                (6, 23, SimpleCRON.WILDCARD_VALUE, 59, {'bbbw'}),
                (6, 23, 59, 59, {'bbb'})
            ]
        )

        self.simple_cron.remove(callback_name='ccc')
        self.assertEqual(self.simple_cron.callbacks, {'aaa': 'AAA', 'bbb': 'BBB',
                                                      'aaaw': 'AAAW', 'bbbw': 'BBBW'})
        self.assertEqual(
            list(self.simple_cron.list()),
            [
                (SimpleCRON.WILDCARD_VALUE, 3, 2, 1, {'aaaw'}),
                (4, 3, 2, 1, {'aaa'}),
                (6, 23, SimpleCRON.WILDCARD_VALUE, 59, {'bbbw'}),
                (6, 23, 59, 59, {'bbb'})
            ]
        )

        self.simple_cron.remove_all()
        self.assertEqual(self.simple_cron.callbacks, {})
        self.assertEqual(self.simple_cron.time_table, {})

        self.simple_cron.add(callback_name='1', callback='1', seconds=2, minutes=2, hours=3, weekdays=6)
        self.simple_cron.add(callback_name='2', callback='1', seconds=1, minutes=2, hours=3, weekdays=6)  #

        self.simple_cron.add(callback_name='3', callback='1', seconds=1, minutes=3, hours=3, weekdays=6)
        self.simple_cron.add(callback_name='4', callback='1', seconds=1, minutes=1, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='5', callback='1',
                             seconds=1, minutes=2, hours=3, weekdays=SimpleCRON.WILDCARD_VALUE)

        self.simple_cron.add(callback_name='6', callback='1', seconds=1, minutes=2, hours=1, weekdays=6)  #
        self.simple_cron.add(callback_name='7', callback='1', seconds=1, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='8', callback='1', seconds=1, minutes=2, hours=2, weekdays=6)  #

        self.simple_cron.add(callback_name='5x2', callback='1',
                             seconds=1, minutes=2, hours=3, weekdays=SimpleCRON.WILDCARD_VALUE)

        self.simple_cron.add(callback_name='9', callback='1', seconds=1, minutes=2, hours=2, weekdays=2)  #
        self.simple_cron.add(callback_name='10', callback='1', seconds=1, minutes=2, hours=2, weekdays=1)  #
        self.simple_cron.add(callback_name='11', callback='1', seconds=1, minutes=2, hours=2, weekdays=6)  #

        out = list(self.simple_cron.list())
        self.assertEqual(out[0], (SimpleCRON.WILDCARD_VALUE, 3, 2, 1, {'5', '5x2'}))
        self.assertEqual(out[1], (1, 2, 2, 1, {'10'}))
        self.assertEqual(out[2], (2, 2, 2, 1, {'9'}))
        self.assertEqual(out[3], (6, 1, 2, 1, {'6'}))
        self.assertEqual(out[4], (6, 2, 2, 1, {'8', '11'}))
        self.assertEqual(out[5], (6, 3, 1, 1, {'4'}))
        self.assertEqual(out[6], (6, 3, 2, 1, {'7', '2'}))
        self.assertEqual(out[7], (6, 3, 2, 2, {'1'}))
        self.assertEqual(out[8], (6, 3, 3, 1, {'3'}))

        self.simple_cron.remove_all()
        self.assertEqual(
            list(self.simple_cron.list()),
            []
        )

    def test_get_next_time_pointer(self):
        self.simple_cron.remove_all()
        self.assertEqual(self.simple_cron.get_next_pointer(0, 0, 0, 0), None)

        self.simple_cron.add(callback_name='1', callback='1', seconds=2, minutes=2, hours=3, weekdays=6)
        self.simple_cron.add(callback_name='2', callback='1', seconds=1, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='3', callback='1', seconds=1, minutes=3, hours=3, weekdays=6)
        self.simple_cron.add(callback_name='4', callback='1', seconds=1, minutes=1, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='5', callback='1', seconds=1, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='6', callback='1', seconds=1, minutes=2, hours=1, weekdays=6)  #
        self.simple_cron.add(callback_name='7', callback='1', seconds=1, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='8', callback='1', seconds=1, minutes=2, hours=2, weekdays=6)  #
        self.simple_cron.add(callback_name='9', callback='1', seconds=1, minutes=2, hours=2, weekdays=2)  #
        self.simple_cron.add(callback_name='10', callback='1', seconds=1, minutes=2, hours=2, weekdays=1)  #
        self.simple_cron.add(callback_name='11', callback='1', seconds=1, minutes=2, hours=2, weekdays=6)  #

        list_pointers = [x for *x, _ in self.simple_cron.list()]
        # print()
        # for k in range(0, len(list_pointers)):
        #     print(
        #         "%d - %s => %s ( %s )" % (
        #             k,
        #             list_pointers[k - 1],
        #             list_pointers[k],
        #             list(self.simple_cron.get_next_pointer(*list_pointers[k - 1]))
        #         )
        #     )

        self.assertEqual(list(self.simple_cron.get_next_pointer(*list_pointers[-1])), list_pointers[0])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*list_pointers[0])), list_pointers[1])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*list_pointers[1])), list_pointers[2])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*list_pointers[2])), list_pointers[3])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*list_pointers[3])), list_pointers[4])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*list_pointers[4])), list_pointers[5])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*list_pointers[5])), list_pointers[6])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*list_pointers[6])), list_pointers[7])

        self.assertEqual(list(self.simple_cron.get_next_pointer(*[6, 3, 3, 1])), [1, 2, 2, 1])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[1, 2, 2, 1])), [2, 2, 2, 1])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[2, 2, 2, 1])), [6, 1, 2, 1])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[6, 1, 2, 1])), [6, 2, 2, 1])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[6, 2, 2, 1])), [6, 3, 1, 1])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[6, 3, 1, 1])), [6, 3, 2, 1])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[6, 3, 2, 1])), [6, 3, 2, 2])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[6, 3, 2, 2])), [6, 3, 3, 1])

    def test_get_next_time_pointer__wildcard(self):
        self.simple_cron.remove_all()
        self.simple_cron.add(callback_name='1', callback='1', seconds=2, minutes=2, hours=3, weekdays=6)
        self.simple_cron.add(callback_name='2', callback='1', seconds=1, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='3', callback='1', seconds=1, minutes=3, hours=3, weekdays=6)
        self.simple_cron.add(callback_name='4', callback='1', seconds=1, minutes=1, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='5', callback='1', seconds=1, minutes=2, hours=3,
                             weekdays=SimpleCRON.WILDCARD_VALUE)  #
        self.simple_cron.add(callback_name='6', callback='1', seconds=1, minutes=2, hours=1, weekdays=6)  #
        self.simple_cron.add(callback_name='7', callback='1', seconds=1, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='8', callback='1', seconds=1, minutes=2, hours=2, weekdays=6)  #
        self.simple_cron.add(callback_name='9', callback='1', seconds=1, minutes=2, hours=2, weekdays=2)  #
        self.simple_cron.add(callback_name='10', callback='1', seconds=1, minutes=2, hours=2, weekdays=1)  #
        self.simple_cron.add(callback_name='11', callback='1', seconds=1, minutes=2, hours=2, weekdays=6)  #

        list_pointers = [x for *x, _ in self.simple_cron.list()]
        # print()
        # for k in range(0, len(list_pointers)):
        #     print(
        #         "W %d - %s => %s ( %s )" % (
        #             k,
        #             list_pointers[k - 1],
        #             list_pointers[k],
        #             list(self.simple_cron.get_next_pointer(*list_pointers[k - 1]))
        #         )
        #     )

        self.assertEqual(list(self.simple_cron.get_next_pointer(*[6, 3, 3, 1])), [0, 3, 2, 1])  # Wildcard
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[0, 3, 2, 1])), [1, 2, 2, 1])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[1, 2, 2, 1])), [1, 3, 2, 1])  # Wildcard
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[1, 3, 2, 1])), [2, 2, 2, 1])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[2, 2, 2, 1])), [2, 3, 2, 1])  # Wildcard
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[2, 3, 2, 1])), [3, 3, 2, 1])  # Wildcard
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[3, 3, 2, 1])), [4, 3, 2, 1])  # Wildcard
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[4, 3, 2, 1])), [5, 3, 2, 1])  # Wildcard
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[5, 3, 2, 1])), [6, 1, 2, 1])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[6, 1, 2, 1])), [6, 2, 2, 1])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[6, 2, 2, 1])), [6, 3, 1, 1])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[6, 3, 1, 1])), [6, 3, 2, 1])  # static and wildcard
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[6, 3, 2, 1])), [6, 3, 2, 2])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[6, 3, 2, 2])), [6, 3, 3, 1])

        self.simple_cron.remove_all()
        self.simple_cron.add(callback_name='xx', callback='XX', seconds=range(0, 59, 10))
        self.assertEqual(self.simple_cron.callbacks, {'xx': 'XX'})
        self.assertEqual(
            list(self.simple_cron.list()),
            [
                (SimpleCRON.WILDCARD_VALUE, SimpleCRON.WILDCARD_VALUE, SimpleCRON.WILDCARD_VALUE, 0, {'xx'}),
                (SimpleCRON.WILDCARD_VALUE, SimpleCRON.WILDCARD_VALUE, SimpleCRON.WILDCARD_VALUE, 10, {'xx'}),
                (SimpleCRON.WILDCARD_VALUE, SimpleCRON.WILDCARD_VALUE, SimpleCRON.WILDCARD_VALUE, 20, {'xx'}),
                (SimpleCRON.WILDCARD_VALUE, SimpleCRON.WILDCARD_VALUE, SimpleCRON.WILDCARD_VALUE, 30, {'xx'}),
                (SimpleCRON.WILDCARD_VALUE, SimpleCRON.WILDCARD_VALUE, SimpleCRON.WILDCARD_VALUE, 40, {'xx'}),
                (SimpleCRON.WILDCARD_VALUE, SimpleCRON.WILDCARD_VALUE, SimpleCRON.WILDCARD_VALUE, 50, {'xx'})
            ]
        )
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[6, 24, 59, 59])), [0, 0, 0, 0])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[0, 0, 0, 0])), [0, 0, 0, 10])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[0, 0, 0, 10])), [0, 0, 0, 20])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[0, 0, 0, 20])), [0, 0, 0, 30])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[0, 0, 0, 30])), [0, 0, 0, 40])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[0, 0, 0, 40])), [0, 0, 0, 50])
        self.assertEqual(list(self.simple_cron.get_next_pointer(*[0, 0, 0, 50])), [0, 0, 1, 0])

    def test_run_callbacks(self):
        self.simple_cron.remove_all()

        OUT = []

        def x(data):
            def y(*args, **kwargs):
                OUT.append(data)

            return y

        self.simple_cron.run_callbacks(second=0, minute=0, hour=0, weekday=0)
        self.assertEqual(OUT, [])
        OUT = []

        self.simple_cron.add(callback_name='1', callback=x('1'), seconds=2, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='2', callback=x('2'), seconds=1, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='3', callback=x('3'), seconds=1, minutes=3, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='4', callback=x('4'), seconds=1, minutes=1, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='5', callback=x('5'), seconds=1, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='6', callback=x('6'), seconds=1, minutes=2, hours=1, weekdays=6)  #
        self.simple_cron.add(callback_name='7', callback=x('7'), seconds=1, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='8', callback=x('8'), seconds=1, minutes=2, hours=2, weekdays=6)  #
        self.simple_cron.add(callback_name='9', callback=x('9'), seconds=1, minutes=2, hours=2, weekdays=2)  #
        self.simple_cron.add(callback_name='10', callback=x('10'), seconds=1, minutes=2, hours=2, weekdays=1)  #
        self.simple_cron.add(callback_name='11', callback=x('11'), seconds=1, minutes=2, hours=2, weekdays=6)  #

        # for key, step in enumerate(self.simple_cron.list()):
        #     print(key, step, '+')

        self.simple_cron.run_callbacks(second=1, minute=2, hour=2, weekday=2)
        self.assertEqual(OUT, ['9'])
        OUT = []

        self.simple_cron.run_callbacks(second=1, minute=2, hour=1, weekday=6)
        self.assertEqual(OUT, ['6'])
        OUT = []

        self.simple_cron.run_callbacks(second=1, minute=2, hour=2, weekday=6)
        self.assertEqual(set(OUT), set(['11', '8']))
        OUT = []

        self.simple_cron.run_callbacks(second=1, minute=1, hour=3, weekday=6)
        self.assertEqual(OUT, ['4'])
        OUT = []

        self.simple_cron.run_callbacks(second=1, minute=2, hour=3, weekday=6)
        self.assertEqual(set(OUT), set(['5', '7', '2']))
        OUT = []

        self.simple_cron.run_callbacks(second=2, minute=2, hour=3, weekday=6)
        self.assertEqual(OUT, ['1'])
        OUT = []

        self.simple_cron.run_callbacks(second=1, minute=3, hour=3, weekday=6)
        self.assertEqual(OUT, ['3'])
        OUT = []

    def test_run_callbacks__wildcard(self):
        self.simple_cron.remove_all()

        OUT = []

        def x(data):
            def y(*args, **kwargs):
                OUT.append(data)

            return y

        self.simple_cron.add(callback_name='1', callback=x('1'), seconds=2, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='2', callback=x('2'), seconds=1, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='3', callback=x('3'), seconds=1, minutes=3, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='4', callback=x('4'), seconds=1, minutes=1, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='5', callback=x('5'), seconds=1, minutes=2, hours=3,
                             weekdays=self.simple_cron.WILDCARD_VALUE)  #
        self.simple_cron.add(callback_name='6', callback=x('6'), seconds=1, minutes=2, hours=1, weekdays=6)  #
        self.simple_cron.add(callback_name='7', callback=x('7'), seconds=1, minutes=2, hours=3, weekdays=6)  #
        self.simple_cron.add(callback_name='8', callback=x('8'), seconds=1, minutes=2, hours=2, weekdays=6)  #
        self.simple_cron.add(callback_name='9', callback=x('9'), seconds=1, minutes=2, hours=3, weekdays=2)  #
        self.simple_cron.add(callback_name='10', callback=x('10'), seconds=1, minutes=2, hours=2, weekdays=1)  #
        self.simple_cron.add(callback_name='11', callback=x('11'), seconds=1, minutes=2, hours=2, weekdays=6)  #

        # for key, step in enumerate(self.simple_cron.list()):
        #     print(key, step, '+')

        self.simple_cron.run_callbacks(second=1, minute=2, hour=3, weekday=2)
        self.assertEqual(set(OUT), set(['9', '5']))
        OUT = []

        self.simple_cron.run_callbacks(second=1, minute=2, hour=1, weekday=6)
        self.assertEqual(OUT, ['6'])
        OUT = []

        self.simple_cron.run_callbacks(second=1, minute=2, hour=2, weekday=6)
        self.assertEqual(set(OUT), set(['11', '8']))
        OUT = []

        self.simple_cron.run_callbacks(second=1, minute=1, hour=3, weekday=6)
        self.assertEqual(OUT, ['4'])
        OUT = []

        self.simple_cron.run_callbacks(second=1, minute=2, hour=3, weekday=6)
        self.assertEqual(set(OUT), set(['5', '7', '2']))
        OUT = []

        self.simple_cron.run_callbacks(second=2, minute=2, hour=3, weekday=6)
        self.assertEqual(OUT, ['1'])
        OUT = []

        self.simple_cron.run_callbacks(second=1, minute=3, hour=3, weekday=6)
        self.assertEqual(OUT, ['3'])
        OUT = []

    def test_time_change_correction(self):
        sc = SimpleCRON()

        sc.time_change = 300

        sc.get_time_change_pointer = lambda: 300
        self.assertEqual(sc.get_time_change_correction(0), 0)

        sc.get_time_change_pointer = lambda: 400
        self.assertEqual(sc.get_time_change_correction(0), -100)

        sc.get_time_change_pointer = lambda: 500
        self.assertEqual(sc.get_time_change_correction(0), -200)

        sc.get_time_change_pointer = lambda: 600
        self.assertEqual(sc.get_time_change_correction(0), -300)

        sc.get_time_change_pointer = lambda: 700
        self.assertEqual(sc.get_time_change_correction(0), -400)

        sc.get_time_change_pointer = lambda: 800
        self.assertEqual(sc.get_time_change_correction(0), -500)

        sc.get_time_change_pointer = lambda: 900
        self.assertEqual(sc.get_time_change_correction(0), -600)

        sc.get_time_change_pointer = lambda: 1000
        self.assertEqual(sc.get_time_change_correction(0), -700)

        sc.get_time_change_pointer = lambda: 100
        self.assertEqual(sc.get_time_change_correction(0), -800)

        sc.get_time_change_pointer = lambda: 200
        self.assertEqual(sc.get_time_change_correction(0), -900)

        sc.get_time_change_pointer = lambda: 299
        self.assertEqual(sc.get_time_change_correction(0), -999)


class TestDecoratorsCRON(unittest.TestCase):

    def test_run_times(self):
        class scron_instance:
            removed = False
            run_times_counter = 0

            @classmethod
            def remove(cls, callback_name):
                cls.removed = True

        memory = {}

        def xcallback(scorn_instance, callback_name, pointer, memory):
            scron_instance.run_times_counter += 1

        callback = run_times(3)(xcallback)

        callback(scron_instance, 'xcallback', (1, 0, 0, 0), memory)
        self.assertEqual(memory, {'__run_times': 1})
        self.assertEqual(scron_instance.run_times_counter, 1)
        self.assertFalse(scron_instance.removed)

        callback(scron_instance, 'xcallback', (1, 0, 0, 0), memory)
        self.assertEqual(memory, {'__run_times': 2})
        self.assertEqual(scron_instance.run_times_counter, 2)
        self.assertFalse(scron_instance.removed)

        callback(scron_instance, 'xcallback', (1, 0, 0, 0), memory)
        self.assertEqual(memory, {'__run_times': 3})
        self.assertEqual(scron_instance.run_times_counter, 3)
        self.assertTrue(scron_instance.removed)

    def test_call_counter(self):
        @call_counter
        def some_call(scorn_instance, callback_name, pointer, memory):
            return memory[call_counter.ID]

        scorn_instance = None
        callback_name = 'abc'
        pointer = (0, 0, 0, 0)
        memory = {}

        self.assertEqual(some_call(scorn_instance, callback_name, pointer, memory), 1)
        self.assertEqual(some_call(scorn_instance, callback_name, pointer, memory), 2)
        self.assertEqual(some_call(scorn_instance, callback_name, pointer, memory), 3)

    def test_time_since_last_call(self):
        import utime

        @time_since_last_call
        def some_call(scorn_instance, callback_name, pointer, memory):
            utime.sleep(1)
            utime.sleep_ms(500)
            return memory[time_since_last_call.ID]

        scorn_instance = None
        callback_name = 'abc'
        pointer = (0, 0, 0, 0)
        memory = {}

        self.assertEqual(some_call(scorn_instance, callback_name, pointer, memory), None)
        sec, msec = some_call(scorn_instance, callback_name, pointer, memory)
        self.assertEqual(sec, 1)
        self.assertTrue(505 > msec >= 500, msg="505 > %d ms >= 500" % msec)


class TestIntegrationTests(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
