import csv
import pprint
import sys
from collections import defaultdict


class NiftyIndexCreator:
    def read_index_symbols(selfi, csv_name):
        print(f"reading csv file '{csv_name}'.")
        columns = defaultdict(list)  # Dictionary to store column data

        with open(csv_name, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                for col_name, value in row.items():
                    if col_name == "Symbol":
                        columns[col_name.lower()].append(value + ".NS")
        return columns["symbol"]

    def write_updated_index(self, csv1, csv2, dest):
        smaller_list = self.read_index_symbols(csv1)
        bigger_list = self.read_index_symbols(csv2)

        print(f"before update index size: {len(bigger_list)}")
        _ = [bigger_list.remove(symbol) for symbol in smaller_list]
        print(f"after update index size: {len(bigger_list)}")

        # write updated index file.
        with open(dest, "w") as file:
            for symbol in bigger_list:
                file.write(symbol + "\n")


if __name__ == "__main__":
    obj = NiftyIndexCreator()
    obj.write_updated_index(sys.argv[1], sys.argv[2], sys.argv[3])
