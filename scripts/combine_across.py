
import pandas as pd
from os import listdir, path
from optparse import OptionParser
import shutil


'''
The goal of this scipt is to combine CSV files, in this case only show ver is suppored
'''


class fileSet(object):

    @staticmethod
    def combineInt(filea, fileb, tableKey):
        pa = pd.read_csv("./output/{0}".format(filea), index_col=tableKey)
        pb = pd.read_csv("./output/{0}".format(fileb), index_col=tableKey)
        # pc = pd.concat([pa, pb], sort=True)
        try:
            pc = pa.append(pb, verify_integrity=True)
        except ValueError as e:
            pass
        else:
            pc.to_csv("./output/{0}".format(filea))


def main():
    parser = OptionParser()
    parser.add_option("-t", "--template", dest="templatef", default="")
    parser.add_option("-s", "--sourcefiletype", dest="sourcefiletype", default="")
    parser.add_option("-k", "--tablekey", dest="tablekey", default="")
    (options, args) = parser.parse_args()
    # filea = "base.csv"
    filea = (options.templatef + "_db.csv")
    shutil.copy("./scripts/{0}".format(options.templatef),
                "./output/{0}".format(filea))
    # match File based on -s and append them to files
    files = []
    [files.append(f) for f in listdir("./output/") if options.sourcefiletype in f]
    # join these files
    for f in files:
        fileSet.combineInt(filea, f, options.tablekey)


if __name__ == "__main__":
    main()

'''
Run this file

python ./scripts/combine_across.py -t show_ver_template.csv -s "_show_ver.log_prs.csv" -k HOSTNAME

reference:
template =  is the base file for pandas, this typically has all the headers(column names in CSV file, see show_ver_template.csv) defined
sourcefiletype = are the source file types you want to match, for example "_show_ver.log_prs.csv" will match all file names that contain that
tableKey - is the table key that will be used to reach the tables

'''