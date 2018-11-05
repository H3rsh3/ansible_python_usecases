import pandas as pd
import re
from os import listdir, path
'''
Script used to validate BGP neigh
run this file from where the csv files are
'''

class StandardSiteValidator(object):
    """docstring for StateValidator
    """

    def __init__(self, device):
        self.device = device

    def bgpNeighValidate(self, bgpTable, inList, minOne=True):
        '''
        bgpTable = parsed BGP table from textfsm template in CSV format
        inList = accepted BGP AS Value, if out of this. the result will be fail
        minOne = musthave atlease one BGP peer, it not will return fail
        '''
        self.inList = inList
        self.minOne = minOne
        validationResult = True
        intRegCheck = re.compile("\\d+")
        try:
            pbgp = pd.read_csv(bgpTable, index_col="BGP_NEIGH")
        except Exception as e:
            raise e
        else:
            #  if the neighbor table is empty, its a nonStarnard sites
            # print("=" * 32)
            if pbgp.empty:
                validationResult = False
            else:
                # cast all values in the dataframe to string
                pbgp_srt = pbgp.applymap(str)
                # iterate through series in column
                for colname, series in pbgp_srt.iterrows():
                    # if the BGP neigh ASN is not 'inList' and is not down
                    if not (series.values[0] in inList) and intRegCheck.match(series.values[1]):
                        validationResult = False
                    else:
                        pass
        # print("{0}:{1}".format(self.device, validationResult))
        return("BGP neigh test passed: {0}".format(validationResult))


class GenerateRepot(object):

    def __init__(self, sites):
        self.sites = sites
        self.reportData = []
        self.testConditions = []

    def addSite(self, site):
        self.sites.append(site)

    def addtestConditions(self, testCondition):
        self.testConditions.append(testCondition)

    def validate(self, validtorChecks):
        pass

    def generateReport(self, resultdata):
        for site in sites:
            sv = StandardSiteValidator(site.split("_")[0])
        print(self.reportData)


if __name__ == "__main__":
    files = []
    [files.append(f) for f in listdir("./") if "_show_bgp_sum.log_prs.csv" in f]
    # bgp_rep = GenerateRepot(sites)
    for site in files:
        sv = StandardSiteValidator(site.split("_")[0])
        print(site.split("_")[0] + sv.bgpNeighValidate(site, ["209", "3549"]))
        # bgp_rep.generateReport.addSite(sv)
    # sv = StandardSiteValidator(site.split("_")[0])

'''
This will fail if the router has one BGP neighbor configured but not up
run script python ./nmg_bgp_check.py > nmg_bgp_check_ouput.csv
'''
