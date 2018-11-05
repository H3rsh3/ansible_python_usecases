import xml.etree.ElementTree as ET
from os import listdir, path
import csv
import ipaddress

'''
This program has the following
    * PaloInterface- contains interface paramaters
    * PaloDevice- has a group of PaloInterface
    * DeviceGroup- a group of PaloDevices
    * ParseIntfBuilder- is used to parse xml documen and output the data as dictionary
        * outputs dict in format{intfname: {intf_paramater_key: intf_paramater_value}}
'''

class PaloInterface(object):

    def __init__(self, intf_name):
        self.intf_name = intf_name
        self.ipv4network = ''

    def addParamDict(self, *argv, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def cleanZoneNames(self, csvdb):
        # this is left out on purpose as this is not a arribte we want to store
        # self.csvdb = csvdb
        with open(csvdb, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for k in reader:
                try:
                    if k['oldname'] == self.zone:
                        self.zone = k['newname']
                except AttributeError:
                    pass
        csvfile.close()

    def setNetworkID(self):
        try:
            a = ipaddress.ip_interface(self.ipv4)
            self.ipv4network = (a.network)
        except ValueError:
            pass
        else:
            pass



class PaloDevice(object):

    def __init__(self, deviceName):
        self.deviceName = deviceName
        self.interfaces = []

    def addInterface(self, paloInterface):
        self.paloInterface = paloInterface
        self.interfaces.append(self.paloInterface)


class DeviceGroup(object):

    def __init__(self, groupname):
        self.groupname = groupname
        self.devices = []

    def addDevice(self, deviceName):
        self.devices.append(deviceName)


class ParseIntfBuilder(object):
    """docstring for ParseIntfBuilder"""

    def __init__(self, xmlfile):
        # Get interface and Helper address
        self.xmlfile = xmlfile
        self.devicename = xmlfile.split('.')[0]
        self.fwinterface = {}
        self.tree = ET.parse(xmlfile)

    def parseIntfHelp(self):
        root = self.tree.getroot()
        int_helper = root.findall('.//dhcp/interface/entry')
        l3_int = {}
        for i in int_helper:
            intf_name = (i.get("name"))
            try:
                # l3_int[intf_name]
                l3_int[intf_name]['helper_address'] = []
            except KeyError:
                l3_int[intf_name] = {}
                l3_int[intf_name]['helper_address'] = []
                pass
                # l3_int['intf_name']['helper_address'] = "test"
            for helpadd in i.iterfind('.//relay/ip/server/member'):
                l3_int[intf_name]['helper_address'].append(helpadd.text)
                # print("{0}:{1}".format(i.get("name"), helpadd.text))
        # self.interface.append(l3_int)
        for k, v in l3_int.items():
            for hk, hv in v.items():
                try:
                    self.fwinterface[k]
                except KeyError:
                    self.fwinterface[k] = {}
                    self.fwinterface[k]['helper_address'] = hv
                else:
                    self.fwinterface[k]['helper_address'] = hv
        # print(self.fwinterface)
        # print(l3_int['vlan.3'])

    def parseIntfZone(self):
        # Get interface and Zone
        root = self.tree.getroot()
        int_zone = root.findall('.//zone/entry')
        l3_int = {}
        for i in int_zone:
            zone = (i.get("name"))
            for intf_name in i.iterfind('.//network/layer3/member'):
                # print(interface)
                try:
                    l3_int[intf_name.text]['zone'] = []
                except KeyError:
                    l3_int[intf_name.text] = {}
                    l3_int[intf_name.text]['zone'] = zone
                # print("{0}:{1}".format(intf_name.text, zone))
        # print(l3_int["vlan.5"]["zone"])
        for k, v in l3_int.items():
            for zk, zv in v.items():
                try:
                    self.fwinterface[k]
                except KeyError:
                    self.fwinterface[k] = {}
                    self.fwinterface[k]['zone'] = zv
                else:
                    self.fwinterface[k]['zone'] = zv
        # print(self.fwinterface)

    def parseIntfVlan(self):
        # Get interface and VLAN
        root = self.tree.getroot()
        int_zone = root.findall('.//network/vlan/entry')
        for i in int_zone:
            # print(i.attrib)
            vlanName = (i.get("name"))
            # Try loop to avoid crash no nonvalues
            try:
                virtInterface = (i.find("./virtual-interface/interface").text)
            except AttributeError:
                virtInterface = "native"
            else:
                pass
            finally:
                physicalInterface = (i.find("./interface/member").text)
                print("{0},{1},{2}".format(vlanName,
                                           virtInterface,
                                           physicalInterface))

    def parseIntfIP(self):
        # Get interface and IP for physical interface
        root = self.tree.getroot()
        eth_fwinterface = root.findall('.//network/interface/ethernet/entry')
        no_name_vlan_fwinterface = root.findall('.//network/interface/vlan')
        vlan_fwinterface = root.findall('.//network/interface/vlan/units/entry')
        l3_int = {}
        for i in eth_fwinterface:
            # print(i.attrib)
            intf_name = (i.get("name"))
            # print(intf_name)
            # Try loop to avoid crash no nonvalues
            try:
                ipaddr = (i.find("./layer3/ip/entry").get("name"))
            except AttributeError:
                ipaddr = "no-ip"
            else:
                pass
            finally:
                try:
                    l3_int[intf_name]['ipv4'] = ipaddr
                except KeyError:
                    l3_int[intf_name] = {}
                    l3_int[intf_name]['ipv4'] = ipaddr
            # print(l3_int)

        # Get intefaces add IP for vlan fwinterface untagged
        for i in no_name_vlan_fwinterface:
            try:
                # print("{0}:{1}".format("vlan", i.find("./ip/entry").get("name")))
                try:
                    l3_int["vlan"]['ipv4'] = i.find("./ip/entry").get("name")
                except KeyError:
                    l3_int["vlan"] = {}
                    l3_int["vlan"]['ipv4'] = i.find("./ip/entry").get("name")
            except AttributeError:
                pass
        # print(l3_int)
        # Get interface and IP for vlan fwinterface tagged
        for i in vlan_fwinterface:
            # print(i.attrib)
            vlan_intfName = (i.get("name"))
            # Try loop to avoid crash no nonvalues
            try:
                vipaddr = (i.find("./ip/entry").get("name"))
            except AttributeError:
                vipaddr = "no-ip"
            else:
        # print(dir(aInterface))
                pass
            finally:
                # print("{0}:{1}".format(vlan_intfName, ipaddr))
                try:
                    l3_int[vlan_intfName]['ipv4'] = vipaddr
                except KeyError:
                    l3_int[vlan_intfName] = {}
                    l3_int[vlan_intfName]['ipv4'] = vipaddr
        # print(l3_int)
        for k, v in l3_int.items():
            for ik, iv in v.items():
                try:
                    self.fwinterface[k]
                except KeyError:
                    self.fwinterface[k] = {}
                    self.fwinterface[k]['ipv4'] = iv
                else:
                    self.fwinterface[k]['ipv4'] = iv

if __name__ == "__main__":
    fileNames = []
    prs_file_suffix = {"xml": ".xml"}
    [fileNames.append(f) for f in listdir("./") if prs_file_suffix['xml'] in f]
    nmgfw = DeviceGroup("nmgDevices")
    for devices in fileNames:
        aParser = ParseIntfBuilder(devices)
        aParser.parseIntfHelp()
        aParser.parseIntfZone()
        # aParser.parseIntfVlan()
        aParser.parseIntfIP()
        # Create a PaloDevice
        aDevice = PaloDevice(devices.split(".")[0])
        for k, v in aParser.fwinterface.items():
            # Create an interface
            aInterface = PaloInterface(k)
            # Pass on dictinary as kwargs to fill dynamically create attributes based on source
            # ** aka double splat, will conver the dict to kwargs
            aInterface.addParamDict(**v)
            aInterface.cleanZoneNames("../firewall_zone_map.csv")
            aInterface.setNetworkID()
            # Add interface to the aDevice
            aDevice.addInterface(aInterface)
        # Add device to the device group
        nmgfw.addDevice(aDevice)
    # Iterate through devices in device group
    csvHeaders = []
    for device in nmgfw.devices:
        with open("fw_{0}.csv".format(device.deviceName), 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csvHeaders)
            # iterate through interface in the device to get all headers
            for intf in device.interfaces:
                for k, v in intf.__dict__.items():
                    if k not in csvHeaders:
                        csvHeaders.append(k)
            # once headers are collected, write headers to file
            writer.writeheader()
            # write each row to the file, pass in all attributes as dictonary
            for intf in device.interfaces:
                writer.writerow(intf.__dict__)

'''
This script takes in a palo alto device's config in XML format and outputs the interface details in CSV format
Put all files that need to be converted in the same dir and run this sciprt
'''