import textfsm
import sys

'''
This script will take raw output from CLI and pass it through texfsm templates
It will also export the texfsm template in CSV format, the file name 
It will append _prs.csv to the parsed file that is exported
this is the local ver of the script to test
'''



class FileObject(object):

    def __init__(self, source_file):
        self.source_file = source_file

    def getRawOutput(self):
        readresults = ""
        try:
            with open("../output/{0}".format(self.source_file), "r") as f:
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

    def parseShowRunIntFilt1(self, export=False):
        re_table = textfsm.TextFSM(open("show_int_f_lpip_template"))
        # print(self.FileObject.getRawOutput())
        data = re_table.ParseText(self.FileObject.getRawOutput())
        filename = (self.FileObject.getSourceFilename() + "_parsed.csv")
        headers = (re_table.header)
        if export:
            Writedata.simpleRows(filename, headers, data)
        else:
            return data


class Writedata(object):

    @staticmethod
    def simpleRows(filename, headers, data):
        # print(headers)
        with open("../output/{}".format(filename), 'w') as f:
            f.write(','.join(headers) + "\n")
            for row in data:
                f.write(','.join(row) + "\n")


def runParser(source_file, parser):
    file = FileObject(source_file)
    parsera = UnstrProc(file)
    parsera.parseShowRunIntFilt1(export=True)


if __name__ == "__main__":
    source_file, parser = sys.argv[1], sys.argv[2]
    runParser(source_file, parser)
