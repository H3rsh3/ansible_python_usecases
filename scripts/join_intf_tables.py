
import pandas as pd
import sys

class fileSet(object):

    @staticmethod
    def combineInt(filea, fileb, filec):
        pa = pd.read_csv("./output/{0}".format(filea), index_col="INTERFACE")
        pb = pd.read_csv("./output/{0}".format(fileb), index_col="INTERFACE")
        pc = pa.merge(pb, on="INTERFACE")
        pc.to_csv("./output/{0}_joined.csv".format(filec))


if __name__ == "__main__":
    filea, fileb, filec = sys.argv[1], sys.argv[2], sys.argv[3]
    fileSet.combineInt(filea, fileb, filec)