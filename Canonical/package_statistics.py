#!/usr/bin/python

# Used to parse html page to get urls as well as artitecture information
from bs4 import BeautifulSoup
import requests

# Package used for getting CLI options and parsing args
import sys, getopt

# Handling python2 or python3 compactibility
try: #python3
    import urllib.request as req
except: #python2
    import urllib2 as req

"""
Class defined to process top 10 packages that have the most files associated
with artitecture given by user
"""
class PKG_STATS:
    def __init__(self, root_url="", arch=""):
        self.root = root_url
        self.arch = arch

    # Setters
    def set_root(self, root_url):
        self.root = root_url

    def set_arch(self, arch):
        self.arch = arch

        # Getters
    def get_root(self):
        return self.root

    def get_arch(self):
        return self.arch

    def make_pgk_dict_by_arch(self):
        print()





def usage():
    a = "\n\t\t -a or --arch : specify artitecture type \n"
    a_example = "\t\t Example: \n"
    a_example += "\t\t ./package_statistics.py -a amd64 \n"
    a_example += "\t\t ./package_statistics.py  --arch amd64 \n\n\n"
    h = "\n\t\t -h or --help : used to give you options to run this script  \n"
    h_example = "\t\t Example : \n"
    h_example += "\t\t ./package_statistics.py -h \n"
    h_example += "\t\t OR .... \n"
    h_example += "\t\t ./package_statistics.py --help \n"

    return a + a_example + h + h_example

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'h:a', ['arch'])

        if len(opts) == 0:
            print(usage())
            sys.exit(2)
        else:
            for opt in opts:
                # Making sure only one argument is given when -a or --arch options used
                if (opt[0] == "-a" or opt[0] == "--arch") and len(args) == 1:
                    break
                else:
                    print(usage())
                    break
    except getopt.GetoptError:
        #Print a message or do something useful
        print(usage())
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
