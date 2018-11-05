
from optparse import OptionParser


def main():
    parser = OptionParser()
    parser.add_option("-t", "--template", dest="templatef", default="")
    parser.add_option("-s", "--sourcefiletype", dest="sourcefiletype", default="")
    (options, args) = parser.parse_args()
    print(options.templatef)
    print(options.sourcefiletype)

main()