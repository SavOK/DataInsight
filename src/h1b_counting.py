import itertools as itt
import sys

from pathlib import Path
from operator import itemgetter


class Table:
    hardCodedkey = {'OCCUPATIONS': {'SOC_NAME', 'LCA_CASE_SOC_NAME'},
                    'STATUS': {'CASE_STATUS', 'STATUS'},
                    'STATES': {'WORKSITE_STATE', 'LCA_CASE_WORKLOC1_STATE'}}

    def __init__(self, dataFilePath: Path, sep: str = ';', rowNumColumn: str = 'ROW_INDEX',
                 ListToKeep: list = (), ListToDrop: list = (), keysForDataInsightFlag: bool = False):
        """
        Read data from file and convert it to table (list of dictionaries)
        :param dataFilePath: Path to the file
        :param sep: separator default=';'
        :param rowNumColumn: name of the index column
        :param ListToKeep: keys to keep
        :param ListToDrop: keys to dropcd
        :param HardCodedKeysForDataInsightFlag: this is hardcoded part to insure reading of old data
        LCA_CASE
        """
        self.filePath = dataFilePath  # File with data
        self.dataList = []  # Table (list of dictionaries)
        self.keys = self._read_input_file(
            sep=sep, rowNumColumn=rowNumColumn, ListToKeep=ListToKeep,
            ListToDrop=ListToDrop, keysForDataInsightFlag=keysForDataInsightFlag)  # set of columns

    def _check_list_to_keep_and_drop(self, keys: list, ListToKeep: list, ListToDrop: list) -> set:
        """
        check what keys should be dropped from the table
        assertion raised if keep list and drop list are overlapping,
        if key is not present in keys assertion raised
        if all keys are in drop list assertion raised
        :param keys: list of the all keys in table
        :param ListToKeep: list of keys to keep
        :param ListToDrop: list of keys to drop
        :return: set of key to drop from table
        """
        keepSet = set(ListToKeep)
        dropSet = set(ListToDrop)
        keysSet = set(keys)
        assert 0 == len(
            keepSet.intersection(dropSet)), "keep and drop lists are overlapping"  # test if sets are overlapping
        assert 0 == len(
            keepSet.difference(
                keysSet)), f"Not all keep keys are found in table\n{keepSet}\n{keysSet}\n{keepSet.difference(keysSet)}"  # check if all keys are in table
        assert 0 == len(
            dropSet.difference(keysSet)), "Not all drop keys are found in table"  # check if all keys are in table
        assert len(keysSet) != len(dropSet), "drop all keys from table"  # check do not drop all elements from table
        if keepSet:
            return keysSet.difference(keepSet)
        else:
            return dropSet

    def _data_insight_keys(self, keysToTest: list):
        """
        this is hard coded part of the table
        make sure the state key are found in old data to
        {'OCCUPATIONS': {'SOC_NAME'}, 'STATUS': {'CASE_STATUS'},
        'STATES': {'WORKSITE_STATE', 'LCA_CASE_WORKLOC1_STATE'}}
        :param keysToTest:
        """
        for i, key in enumerate(keysToTest):
            for k, v in self.hardCodedkey.items():
                if key in v:
                    keysToTest[i] = k
                    break

    def _break_header_line(self, hLine: str, sep: str, rowNumColumn: str, keysForDataInsightFlag: bool = False) -> list:
        """
        break header line into columns keys
        assertion raised if line is empty or key is not found
        therefore assumes at least 2 columns
        :param hLine: Header line if empty assertion raised
        :param sep: separator default (';')if not found assertion raised
        :param rowNumColumn: add first column name if needed default ("ROW_INDEX")
        :return: list of column names in same order as in test, if column is empty replace it with 'MY_KEY_VAL_#'
        """

        assert 0 != len(hLine), "Empty line"
        assert -1 != hLine.find(sep), "Cannot find sep"

        keys = [s.strip() for s in hLine.split(sep)]
        assert 1 < len(keys), 'Expected at least 2 column'
        if keys[0] == '':
            keys[0] = rowNumColumn
        for x, i in enumerate(keys):
            if i == '':
                keys[x] = f'MY_KEY_VAL_{x}'
        if keysForDataInsightFlag:
            self._data_insight_keys(keys)
        return keys

    def _read_input_file(self, sep: str, rowNumColumn: str,
                         ListToKeep: list, ListToDrop: list, keysForDataInsightFlag: bool = False) -> set:
        """
        reads file in to Table (list of maps) first line is used to make a map keys.
        internal checks are done to make sure file could be opened
        :param sep: separator
        :param rowNumColumn: name of the first column
        :param ListToKeep: list of columns to keep
        :param ListToDrop: list of columns to drop
        :return: set of keys
        """

        # TODO setup missing values to NA

        def drop_keys(D: dict, dropKeys: set):
            """
            removes data from dictionary
            IMPORTANT checks if keys are present done before
            :param D: map to clean
            :param dropKeys: set of keys to drop
            """
            for k in dropKeys:
                del D[k]

        try:
            oF = open(str(self.filePath), 'r', encoding='ISO-8859-1') # to make sure it works on strange excel output
        except FileNotFoundError:
            print(f"Cannot open file {str(self.filePath)}")
            raise

        headerLine = next(oF).strip()
        keys = self._break_header_line(headerLine, sep=sep, rowNumColumn=rowNumColumn,
                                       keysForDataInsightFlag=keysForDataInsightFlag)
        if keysForDataInsightFlag:
            self._data_insight_keys(keys)
            keysToDrop = self._check_list_to_keep_and_drop(keys, list(self.hardCodedkey.keys()), [])
        else:
            keysToDrop = self._check_list_to_keep_and_drop(keys, ListToKeep=ListToKeep, ListToDrop=ListToDrop)
        for line in map(lambda x: x.strip(), oF):
            currDict = {k: v for k, v in zip(keys, line.split(';'))}
            drop_keys(currDict, keysToDrop)
            currDict.update({k: v.strip('\"') for k, v in currDict.items()})  # strip extra \" from the values
            self.dataList.append(currDict)
        oF.close()
        assert len(self.dataList) > 1, "couldn't read any lines from file"

        return self.dataList[0].keys()

    def count_and_percentage_key(self, key: str, certifiedFlag: bool = True) -> list:
        """
        Generates frequency table and percentage
        output sorted based on frequency and key value
        :param key: Column name /key
        :param certifiedFlag: Flag to include only certifiedFlags
        :return: Frequency table (list of dictionaries)
        """
        assert key in self.keys, f"Cannot find key [{key}] in table"
        count_dict = {}
        passed = 0
        if certifiedFlag:
            for D in [D for D in self.dataList if D["STATUS"].upper() == "CERTIFIED"]:
                if not D[key] in count_dict:
                    count_dict[D[key]] = {f'{key}': D[key],
                                          'NUMBER_CERTIFIED_APPLICATIONS': 1,
                                          'PERCENTAGE': 0}
                else:
                    count_dict[D[key]]['NUMBER_CERTIFIED_APPLICATIONS'] += 1
                passed += 1
        else:
            for D in self.dataList:
                if not D[key] in count_dict:
                    count_dict[D[key]] = {f'{key}': D[key],
                                          'NUMBER_CERTIFIED_APPLICATIONS': 1,
                                          'PERCENTAGE': 0}
                else:
                    count_dict[D[key]]['NUMBER_CERTIFIED_APPLICATIONS'] += 1
                passed += 1

        def percent(val, total):
            return float(val) / total * 100.

        # Calculate percent
        [D.update(
            {'PERCENTAGE': percent(D['NUMBER_CERTIFIED_APPLICATIONS'], passed)}) for D in
            count_dict.values()]  # TODO parallel

        L = sorted(count_dict.values(), key=itemgetter(f'{key}'))
        return sorted(L, key=itemgetter('NUMBER_CERTIFIED_APPLICATIONS'), reverse=True)


def write_top_table(top_data: list, outFilePath: Path, topKey: str, topCount: int = 10):
    """
    output table in to file
    :param top_data: table (list of dictionaries)
    :param outFilePath: Path to the output file
    :param topKey: key to be sorted on and header
    :param topCount: the number of lines to be outputted
    """
    assert len(top_data) > 1, 'List is empty'
    assert topKey in top_data[0], f'Cannot find key [{topKey}]'
    with open(str(outFilePath), "w") as oFile:
        header = f"TOP_{topKey};NUMBER_CERTIFIED_APPLICATIONS;PERCENTAGE"
        oFile.write(header + '\n')
        for l in itt.islice(top_data, topCount):
            strO = f"{l[topKey]};{l['NUMBER_CERTIFIED_APPLICATIONS']};{l['PERCENTAGE']:.1f}%"
            oFile.write(strO + '\n')


if __name__ == '__main__':
    # TODO Write checks for the input format
    # TODO Write check to make sure output directory exist
    # TODO Write input optional arguments such as sep or counting columns

    inDataFile = Path(sys.argv[1])
    outOccupationsFile = Path(sys.argv[2])
    outStateFile = Path(sys.argv[3])

    T = Table(inDataFile, keysForDataInsightFlag=True)

    TOP_OCCUPATIONS = T.count_and_percentage_key("OCCUPATIONS")
    TOP_STATES = T.count_and_percentage_key('STATES')

    write_top_table(TOP_OCCUPATIONS, outOccupationsFile, "OCCUPATIONS")
    write_top_table(TOP_STATES, outStateFile, "STATES")
