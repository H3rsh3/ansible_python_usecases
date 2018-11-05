import textfsm
import sys


'''
This script will take raw output from CLI and pass it through texfsm templates
It will also export the texfsm template in CSV format, the file name 
It will append _prs.csv to the parsed file that is exported
'''


class FileObject(object):

    def __init__(self, source_file):
        self.source_file = source_file

    def getRawOutput(self):
        readresults = ""
        try:
            with open("./output/{0}".format(self.source_file), "r") as f:
                readresults = f.read()
                f.close()
        except Exception as e:
            raise e
        else:
            return readresults

    def getSourceFilename(self):
        return(self.source_file)


class UnstrProc(object):

    def __init__(self, FileObject):
        self.FileObject = FileObject

    def parse(self, parser, export=False, complex=True):
        self.parser = parser
        complex_parsers = ["show_run_f_int_template"]
        if parser in complex_parsers:
            complex = True
        #
        re_table = textfsm.TextFSM(open("./scripts/{}".format(self.parser)))
        # print(self.FileObject.getRawOutput())
        data = re_table.ParseText(self.FileObject.getRawOutput())
        filename = (self.FileObject.getSourceFilename() + "_prs.csv")
        headers = (re_table.header)
        # 
        if export:
            if complex:
                Writedata.complexRows(filename, headers, data)
            else:
                Writedata.simpleRows(filename, headers, data)
        else:
            return data


class Writedata(object):

    @staticmethod
    def simpleRows(filename, headers, data):
        # print(headers)
        with open("./output/{}".format(filename), 'w') as f:
            f.write(','.join(headers) + "\n")
            for row in data:
                f.write(','.join(row) + "\n")

    @staticmethod
    def complexRows(filename, headers, data):
        # print(headers)
        # this will convert all lists within the list to string and join them with "|"
        # making the output CSV friendly
        for row in data:
            for n, i in enumerate(row):
                if type(row[n]) == list:
                    row[n] = ("|".join(row[n]))
                elif type(row[n]) == str:
                    row[n] = (row[n].replace(",", "|"))

        with open("./output/{}".format(filename), 'w') as f:
            f.write(','.join(headers) + "\n")
            for row in data:
                f.write(','.join(row) + "\n")

def runParser(source_file, parser):
    file = FileObject(source_file)
    parsera = UnstrProc(file)
    parsera.parse(parser, export=True)


if __name__ == "__main__":
    source_file, parser = sys.argv[1], sys.argv[2]
    runParser(source_file, parser)
