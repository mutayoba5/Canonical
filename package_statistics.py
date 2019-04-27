#! /usr/bin/python

import sys
import getopt
import logging
import gzip
import operator
import requests
from bs4 import BeautifulSoup


try: #python2
    import StringIO as io_proc
    from urllib import urlopen
except:
    import io as io_proc
    from urllib.request import  urlopen

#  Startlogging
logging.basicConfig(filename='PKG_STATS_TOOL.log', filemode='a',
                    format='%(asctime)s : %(name)s - %(levelname)s - %(message)s')

class PackageStats:

    """
    Class defined to process top 10 packages that have the most files associated
    with artitecture given by user
    """

    def __init__(self, root_url="", arch=""):
        self.root = root_url
        self.arch = arch #user input archtecture
        self.compressed_links = [] #list of link to later help download the .gz files
        self.pkg_file_count_dict = {} # Dictionary to aid wit out stats
                                # {package_name : file count (int)}

    # Statistical evalutions
    def evaluate(self, pkg):
        """
        Evaluae fucntion is used to add the file count by one give the mapping
        package_name : file count (int)}
        input is package name
        """
        try:
            _l = long(1) # Used for type comparisons
            if isinstance(self.pkg_file_count_dict[pkg]) == isinstance(_l):
                self.pkg_file_count_dict[pkg] += long(1)
            else:
                self.pkg_file_count_dict[pkg] = long(1)
        except Exception as _e:
            self.pkg_file_count_dict[pkg] = long(1)
            #print(str(e))


    def answers_you_seek(self, top_total_to_display=10):
        """
        Function to dislay the results of the top x amount of results in a
        format that is :
        1. <package name >      <number of files>
        """
        # This turns to a list of pairs
        sorted_dict = sorted(self.pkg_file_count_dict.items(), key=
                             operator.itemgetter(1))
        # Thus able to get top 10 results in descending order
        sorted_dict.reverse()
        cnt = 1 # Used to only display ten results
        for i in sorted_dict:
            print "{:3}. {:30} \t\t {}".format(cnt, i[0], i[1]) # Results display
            if cnt >= top_total_to_display:
                break
            cnt += 1


    # Setters
    def set_root(self, root_url):
        """
        Set root mirror url
        """
        self.root = root_url

    def set_arch(self, arch):
        """
        Set artitecture given by user via CLI
        """
        self.arch = arch

    def set_compressed_links(self, links):
        """
        Set the links found associted wuth the user input and .gz files on
        mirror archive
        """
        self.compressed_links = links

        # Getters
    def get_root(self):
        """
        Return the mirror url
        """
        return self.root

    def get_arch(self):
        """
        Return teh artitecture from user input
        """
        return self.arch

    def get_compressed_links(self):
        """
        Return the compressed_links
        """
        return self.compressed_links


    def is_downloadable(self, url):
        """
        Does the url contain a downloadable resource
        Source: https://www.codementor.io/aviaryan/downloading-files-from-urls-
        in-python-77q3bs0un
        """
        _h = requests.head(url, allow_redirects=True)# Logging

        header = _h.headers
        content_type = header.get('content-type')
        if 'text' in content_type.lower():
            return False
        if 'html' in content_type.lower():
            return False
        return True


    def downloader(self, url):
        """
        Package Downloader
        Takes in url and returns compressed file or list of arch related
        urls
        """
        if self.is_downloadable(url):
            # if true then it is a compressed file
            #print("In downloadable")
            pass
        else:
            # It is html or text which in context is initial source of compressed
            # files urls for given archtitecture argument
            self.scrap_compressed_urls()
        return


    def scrap_compressed_urls(self):
        #print("IN link fetch")
        """
        Uses mirror url to get the links needed for compressed files download
        return: list of compressed links
        """
        links = []
        page = requests.get(self.get_root())
        if page.ok:
            # Traverse to find the body tag
            soup = BeautifulSoup(page.content, "html.parser")
            html = list(soup.children)[0]
            body = list(html.children)[3]

            # Get all the a tags that have actual links
            for _a in body.find_all("a", href=True):
                # Debate to use re.searc but left room fro search flexibility
                if (("Contents-"+self.arch) in str(_a)) or \
                (("Contents-udeb-" + self.arch) in str(_a)):
                    links.append(str(self.root + _a['href']))
            self.set_compressed_links(links)
        else:
            logs("warning",
                 "The request to url: {} did not respond with Response 200".format(self.get_root()))
            exit(1)

    def process_compressed_files(self):
        """
        Downloads and parses through the .gz files via a buffer
        """
        print"processing top ten packages in .... {} \n".format(self.get_arch())
        print"Please wait...."
        try:
            for link in self.get_compressed_links():
                req = urlopen(str(link)) # Download a .gz file
                buf = io_proc.StringIO(req.read()) # make teh downloade file a buffer
                _f = gzip.GzipFile(fileobj=buf) # Now we can unzip the buffer to readable data
                for line in _f.readlines():
                    for i in line.split()[1].split(","): # Parsing the data
                        self.evaluate(i.split("/")[-1]) # Paking key value pair to dic
                req.close()# Clsoe communication
        except Exception as _e:
            logs("warning", _e)
            exit(1)


# END OF CLASS PKG_STATS




# Helper functions

def usage():
    """
    Function used to display help menu for user if given invalid args in CLI
    """
    _a = "\n\t\t -a or --arch : specify artitecture type \n"
    a_example = "\t\t Example: \n"
    a_example += "\t\t ./package_statistics.py -a amd64 \n"
    a_example += "\t\t ./package_statistics.py  --arch amd64 \n\n\n"
    _h = "\n\t\t -h or --help : used to give you options to run this script  \n"
    h_example = "\t\t Example : \n"
    h_example += "\t\t ./package_statistics.py -h \n"
    h_example += "\t\t OR .... \n"
    h_example += "\t\t ./package_statistics.py --help \n"

    return _a + a_example + _h + h_example


def cli_argv(argv):
    """
    Parse the CLI argumnets given by user of this tool
    input: Commandline sys.argv without the enviromental path
    returns: the only argument passed which will be the artitecture
    """
    try:
        opts, args = getopt.getopt(argv, 'h:a', ['arch'])

        if not opts:
            print usage()
            sys.exit(2)
            return None
        else:
            for opt in opts:
                # Making sure only one argument is given when -a or --arch options used
                if (opt[0] == "-a" or opt[0] == "--arch") and len(args) == 1:
                    return args
                else:
                    print usage()
                    break
    except getopt.GetoptError:
        #Print a message or do something useful
        print usage()
        sys.exit(2)


def logs(level, message):
    """
    Logging function to aid with ease of logging the errors and processes
    input vars can be a level which is either warning,error, or infor or critical as
    well as a message to tell what one is logging be it a stack from exception
    or so.
    """
    if level == "info":
        # This is not working as expected , thus will come back to it later
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    elif level == "critical":
        logging.critical(message)
    else:
        logging.error(message)


def main(argv):
    """
    Function used to run the tool
    """
    # Tracking logs
    logs("warning", "Starting package_statistics tool")
    # Main mirror to use ofr getting our stats resources
    _mirror = "http://ftp.uk.debian.org/debian/dists/stable/main/"
    args = cli_argv(argv)
    if not args:
        logs("warning", "An issue occurred that inhibits the tool from getting \
        the artitecture value given!")
        sys.exit(2)

    stats = PackageStats()
    stats.set_root(_mirror)
    stats.set_arch(args[0])
    stats.downloader(_mirror) # Getintial links for compressed sources
    stats.process_compressed_files()
    stats.answers_you_seek()

    logs("warning", "Finished processing package_statistics tool")




if __name__ == "__main__":
    main(sys.argv[1:])
