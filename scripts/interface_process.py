import csv
import ipaddress
from os import listdir, path
from collections import OrderedDict
import pandas as pd
from optparse import OptionParser


class RtrInterface(object):

    def __init__(self, intf_name):
        self.INTERFACE = intf_name
        self.intfState = True
        self.intfType = ""
        self.VRRP_Prioriry = 105
        self.VRRP_ID = int(0)
        self.device = ""
        self.ipv4network = ""
        self.export = True

    def addParamDict(self, *argv, **kwargs):
        self.device = "router"
        # 
        for key, value in kwargs.items():
            setattr(self, key, value)


    def checkStateforExport(self):
        '''
        use strict mathes to determine that ultimate intf state
        '''
        if "down" in self.LINK_STATUS or "down" in self.PROTOCOL_STATUS:
            self.export = False
        else:
            self.export = True

    def ipaddToObj(self):
        '''
        converts IP_ADDRESSM to ipaddress object
        '''
        try:
            # self.IP_ADDRESSM = ipaddress.ip_interface(self.IP_ADDRESSM)
            self.IP_ADDRESSM = ipaddress.IPv4Interface(self.IP_ADDRESSM)
        except ValueError:
            pass
        else:
            pass

    def set_intfType(self):
        '''
        sets interface type to either(p2p, guest, legacy, user)
        if the intfType is blank, it does not have an ip address
        '''
        try:
            #  /30 and private and not subint .250
            if (self.IP_ADDRESSM._prefixlen >= 30 and
                self.IP_ADDRESSM.is_private and "250" not in self.INTERFACE):
                self.intfType = "p2p"
            #  /30 and private and not subint .250
            elif (self.IP_ADDRESSM._prefixlen >= 30 and
                  self.IP_ADDRESSM.is_private and "250" in self.INTERFACE):
                self.intfType = "guest"
            # /32 and loopback
            elif (self.IP_ADDRESSM._prefixlen == 32 and
                  "Loopback" in self.INTERFACE):
                self.intfType = "legacy"
            # Tunnel
            elif ("Tunnel" in self.INTERFACE):
                self.intfType = "legacy"
            # /30 and public
            elif (self.IP_ADDRESSM._prefixlen >= 30 and
                  not self.IP_ADDRESSM.is_private):
                self.intfType = "legacy"
            else:
                self.intfType = "user"
        except AttributeError:
            pass

    def genACLAssignment(self, siteType):
        '''
        determie what ACLs to in which interface
        '''
        try:
            acl = aclAssignment.getAssignment("AAA_Avaya", int(float(self.VLAN_TAG)))
            self.Access_list_IN = acl['Access_list_IN']
            self.Access_list_OUT = acl['Access_list_OUT']
        except ValueError:
            pass

    def setVRRP(self):
        '''
        set VRRP info
        '''
        self.VIP = self.IP_ADDRESSM
        # increment existing IP
        if self.intfType == "user" and self.IP_ADDRESSM._prefixlen < 30:
            try:
                ###### need to implement boundries
                self.IP_ADDRESSM = ipaddress.IPv4Interface("{0}/{1}".format(self.IP_ADDRESSM.ip + 1, self.IP_ADDRESSM._prefixlen))
            except TypeError:
                pass
            try:
                self.VRRP_ID = int(float(self.VLAN_TAG))
            except ValueError:
                self.VRRP_ID = int(0)
                pass

    def setNetworkID(self):
        '''
        identify the network id and mask for the interface, which can be used for routing
        '''
        try:
            # a = ipaddress.ip_interface(self.IP_ADDRESSM)
            self.ipv4network = (self.IP_ADDRESSM.network)
        except (ValueError, AttributeError):
            pass
        else:
            pass


class AniraInterface(RtrInterface):

    def __init__(self, intf_name):
        RtrInterface.__init__(self, intf_name)
        self.VRRP_Prioriry = 110

    def addParamDict(self, *argv, **kwargs):
        self.device = "anira"
        # 
        for key, value in kwargs.items():
            setattr(self, key, value)

    def setVRRP(self):
        '''
        set VRRP info
        '''
        self.VIP = self.IP_ADDRESSM
        # increment existing IP
        if self.intfType == "user" and self.IP_ADDRESSM._prefixlen < 30:
            try:
                ###### need to implement boundries
                self.IP_ADDRESSM = ipaddress.IPv4Interface("{0}/{1}".format(self.IP_ADDRESSM.ip + 2, self.IP_ADDRESSM._prefixlen))
                self.IP_ADDRESSM = self.IP_ADDRESSM
            except TypeError:
                pass
            try:
                self.VRRP_ID = int(float(self.VLAN_TAG))
            except ValueError:
                pass


class RtrDevice(object):

    def __init__(self, deviceName):
        self.deviceName = deviceName
        # self.siteType = siteType
        self.interfaces = []

    def addInterface(self, RtrInterface):
        self.RtrInterface = RtrInterface
        self.interfaces.append(self.RtrInterface)

    def analyzeInterfaces(self):
        for intf in self.interfaces:
            intf.checkStateforExport()
            # Move these out
            intf.ipaddToObj()
            intf.set_intfType()
            # intf.genACLAssignment(1)
            intf.setVRRP()
            intf.setNetworkID()


class DeviceGroup(object):

    def __init__(self, groupname):
        self.groupname = groupname
        self.devices = []

    def addDevice(self, deviceName):
        self.devices.append(deviceName)


class aclAssignment(object):

    @staticmethod
    def getAssignment(siteType, VLAN_TAG):
        '''
        needs csv file with mapping of old and new alcs("AAA_Avaya", 104)
        run in manually like, # print(aclAssignment.getAssignment("AAA_Avaya", 104))`
        siteType- string for site type one from csv
        VLAN_TAG- int for VLAN ID
        returns a dictionary
        '''
        Access_list_IN = ''
        Access_list_OUT = ''
        with open("db_acl_entries.csv", 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for k in reader:
                # print(type(k['VLAN_TAG']))
                if (k['siteType'] == siteType and
                    int(k['VLAN_TAG']) == VLAN_TAG):
                    # set in string
                    if k["Access_list_IN"] != "":
                        Access_list_IN = ("{0}_{1}".format(
                                          k["Access_list_IN"],
                                          k["ACL_ver"]))
                    # set out string
                    if k["Access_list_OUT"] != "":
                        Access_list_OUT = ("{0}_{1}".format(
                                           k["Access_list_OUT"],
                                           k["ACL_ver"]))
        return{'Access_list_IN': Access_list_IN, "Access_list_OUT": Access_list_OUT}

class Writedata(object):

    @staticmethod
    def simpleRows(filename, headers, data):
        # print(headers)
        with open("{}".format(filename), 'w') as f:
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

def main():
    parser = OptionParser()
    parser.add_option("-s", "--rtrIntfFile_joined", dest="rtrIntfFile_joined")
    (options, args) = parser.parse_args()
    # rtrIntfFile_joined = "rtr210_intf_joined.csv"
    destination_file = options.rtrIntfFile_joined.split(".")[0] + "_proc" + ".csv"
    #
    aDeviceGroup = DeviceGroup("nmgRTR")
    aRtrDevice = RtrDevice(options.rtrIntfFile_joined.split("_")[0])
    headerwritten = 0   # track if header is written,once it it, it will not be written again
    # Read through each row DictReader will provide dict with Col: row and add to object
    with open("./output/{0}".format(options.rtrIntfFile_joined), 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for k in reader:
            # print(type(k))
            try:
                aRtrInterface = RtrInterface(k["INTERFACE"])
                aAniraInterface = AniraInterface(k["INTERFACE"])
            except Exception as e:
                raise e
            else:
                aRtrInterface.addParamDict(**k)
                aAniraInterface.addParamDict(**k)
                aRtrDevice.addInterface(aRtrInterface)
                aRtrDevice.addInterface(aAniraInterface) # for simplicy add anira interface to same device
    # proceess interfaces
    aDeviceGroup.addDevice(aRtrDevice)
    for router in aDeviceGroup.devices:
        router.analyzeInterfaces()
        # write to file
        with open("./output/{0}".format(destination_file), 'w') as csv_file:
            for intf in router.interfaces:
                fieldnames = intf.__dict__.keys()
                # loop to write header only once
                if headerwritten == 0:
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    headerwritten = 1
                else:
                    pass
                # loop to only export marked("export": True) interface
                if intf.__dict__["export"]:
                    writer.writerow(intf.__dict__)
                # writer.writerow(intf.__dict__)

if __name__ == "__main__":
    main()