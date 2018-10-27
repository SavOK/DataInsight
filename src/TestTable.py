import unittest
from pathlib import Path
import re
from src.h1b_counting import Table


class TestCheckListToKeepAndDrop(unittest.TestCase):
    WorkPath = Path("/Users/saveliy/DataInsight")
    testInput = WorkPath / "insight_testsuite/test_1/input/h1b_input.csv"
    inputDict = {'keys': ['A', 'B', 'C', 'D', 'E', 'F'],
                 'ListToKeep': ['A', 'B', 'C'],
                 'ListToDrop': ['E', 'D']}

    T = Table(testInput)

    def test_keep_and_drop_overlapping(self):
        with self.assertRaises(AssertionError):
            self.T._check_list_to_keep_and_drop(self.inputDict['keys'], ['A', 'B', 'C'], ['C', 'D'])

    def test_key_not_found(self):
        with self.assertRaises(AssertionError):
            self.T._check_list_to_keep_and_drop(self.inputDict['keys'], ['Z'], ['C', 'D'])
        with self.assertRaises(AssertionError):
            self.T._check_list_to_keep_and_drop(self.inputDict['keys'], ['A'], ['C', 'D', 'L'])

    def test_drop_all_keys(self):
        with self.assertRaises(AssertionError):
            self.T._check_list_to_keep_and_drop(self.inputDict['keys'], [], self.inputDict['keys'])

    def test_nothing_to_drop_and_keep(self):
        correct = set()
        result = self.T._check_list_to_keep_and_drop(self.inputDict['keys'], [], [])
        self.assertSetEqual(correct, result)

    def test_drop(self):
        correct = set(self.inputDict['ListToDrop'])
        result = self.T._check_list_to_keep_and_drop(self.inputDict['keys'], [], self.inputDict['ListToDrop'])
        self.assertSetEqual(correct, result)

    def test_keep(self):
        correct = {'C', 'D', 'E', 'F'}
        result = self.T._check_list_to_keep_and_drop(self.inputDict['keys'], ['A', 'B'], [])
        self.assertSetEqual(correct, result)

    def test_correct_input(self):
        correct = {'D', 'E', 'F'}
        result = self.T._check_list_to_keep_and_drop(**self.inputDict)
        self.assertSetEqual(correct, result)


class TestHeadLine(unittest.TestCase):
    WorkPath = Path("/Users/saveliy/DataInsight")
    testInput = WorkPath / "insight_testsuite/test_1/input/h1b_input.csv"
    T = Table(testInput)

    inputDict = {'one_sep': ['K1;K2', ';K1', 'K2;'],
                 'index_row': {'hLine': ";K1;K2;", 'rowNumColumn': 'idx'},
                 'key_to_find': {'hLine': ";LAMA_ECHO_K;LAMA_KAMA_P;KEEP_M",
                                 'rowNumColumn': 'idx', 'sep': ';',
                                 'keysToFind': ['ECHO_K', 'KAMA_P']}}
    correctDict = {'one_sep': [['K1', 'K2'], ['ROW_INDEX', 'K1'], ['K2', 'MY_KEY_VAL_1']],
                   'index_row': ['idx', 'K1', 'K2', 'MY_KEY_VAL_3'],
                   'keys_to_find': ['idx', 'ECHO_K', 'KAMA_P', 'KEEP_M']}

    def test_empty_line_or_no_sep(self):
        with self.assertRaises(AssertionError):
            self.T._break_header_line("", ';', "ROW_INDEX", [])
        with self.assertRaises(AssertionError):
            self.T._break_header_line("sadasd", ';', 'ROW_INDEX', [])

    def test_one_sep(self):
        for input, corr in zip(self.inputDict['one_sep'], self.correctDict['one_sep']):
            result = self.T._break_header_line(input, ';', 'ROW_INDEX', [])
            self.assertListEqual(corr, result)

    def test_index_row(self):
        corr = self.correctDict['index_row']
        result = self.T._break_header_line(**self.inputDict['index_row'], sep=';', keysToFind=[])
        self.assertListEqual(corr, result)

    def test_keys_found_and_changed(self):
        corr = self.correctDict['keys_to_find']
        result = self.T._break_header_line(**self.inputDict['key_to_find'])
        self.assertListEqual(corr, result)


class TestReadInputFile(unittest.TestCase):
    def test_cannot_open_file(self):
        with self.assertRaises(FileNotFoundError):
            T = Table(Path('/path/to/some/silly/file.txt'))


if __name__ == '__main__':
    unittest.main()
