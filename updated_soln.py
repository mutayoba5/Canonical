#!/usr/bin/python

# Used to parse html page to get urls as well as artitecture information
from bs4 import BeautifulSoup
import requests
import gzip

# Logging
import logging

# Package used for getting CLI options and parsing args
import sys, getopt

try: #python2
    import StringIO as io_proc
    from urllib import urlopen
except:
    import io as io_proc
    from urllib.request import  urlopen

#  Startlogging
logging.basicConfig(filename='PKG_STATS_TOOL.log', filemode='a',
format='%(asctime)s : %(name)s - %(levelname)s - %(message)s')

class PKG_STATS:

    """
    Class defined to process top 10 packages that have the most files associated
    with artitecture given by user
    """

    def __init__(self, root_url="", arch=""):
        self.root = root_url
        self.arch = arch
        self.compressed_links = []
        self.pkg_file_count_dict = {} # Dictionary to aid wit out stats
                                # {package_name : file count (int)}

    # Statistical evalutions
    def evaluate(self, pkg_names_list):
        """
        Evaluae fucntion is used to add the file count by one give the mapping
        package_name : file count (int)}
        input is package name and file list
        """
        for pkg in pkg_names_list:
            if pkg in self.pkg_file_count_dict.keys():
                self.pkg_file_count_dict[pkg] += 1
            else:
                self.pkg_file_count_dict[pkg] = 1


    def answers_you_seek(self, top_total_to_display=10):
        """
        Function to dislay the results of the top x amount of results in a
        format that is :
        1. <package name >      <number of files>
        """
        # This turns to a list of pairs
        sorted_dict = sorted(self.pkg_file_count_dict.items(), key=
        lambda kv:(kv[1], kv[0]))
        cnt = 1
        for i in sorted_dict:
            print(i)
            print("{}. {} \t\t {}".format(cnt, i[0], i[1]))
            if cnt > top_total_to_display: break
            cnt += 1


    # Setters
    def set_root(self, root_url):
        self.root = root_url

    def set_arch(self, arch):
        self.arch = arch

    def set_compressed_links(self, links):
        self.set_compressed_links = links

        # Getters
    def get_root(self):
        return self.root

    def get_arch(self):
        return self.arch

    def get_compressed_links(self):
        return self.set_compressed_links


    def is_downloadable(self,url):
        """
        Does the url contain a downloadable resource
        Source: https://www.codementor.io/aviaryan/downloading-files-from-urls-in-python-77q3bs0un
        """
        h = requests.head(url, allow_redirects=True)# Logging

        header = h.headers
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
            print("In downloadable")
        else:
            # It is html or text which in context is initial source of compressed
            # files urls for given archtitecture argument
            self.scrap_compressed_urls()
        return


    def scrap_compressed_urls(self):
        """
        Uses mirror url to get the links needed for compressed files download
        return: list of compressed links
        """
        links = []
        page = requests.get(self.get_root())
        if page.ok:
            soup = BeautifulSoup(page.content, "html.parser")
            #print([type(item) for item in list(soup.children)])
            html = list(soup.children)[0]
            body = list(html.children)[3]

            for a in body.find_all("a", href=True):
                #print("Contents-"+self.arch)
                if (("Contents-"+self.arch) in str(a)) or (("Contents-udeb-"+self.arch) in str(a)):
                    links.append(str(self.root + a['href']))
            self.set_compressed_links(links)
        else:
            logs("warning",
            "The request to url: {} did not respond with Response 200".format(self.get_root()))
            exit(1)

    def process_compressed_files(self):
        try:
            for link in self.get_compressed_links():
                req = urlopen(str(link))
                buf = io_proc.StringIO(req.read())
                f = gzip.GzipFile(fileobj=buf)
                for line in f.readlines():
                    pkg_name = [i.split("/")[-1] for i in line.split()[1].split(",")]
                    self.evaluate(pkg_name)
                req.close()

        except Exception as e:
            logs("warning",e)
            exit(1)


# END OF CLASS PKG_STATS




# Helper functions

def usage():
    """
    Function used to display help menu for user if given invalid args in CLI
    """
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


def CLI_argv(argv):
    """
    Parse the CLI argumnets given by user of this tool
    input: Commandline sys.argv without the enviromental path
    returns: the only argument passed which will be the artitecture
    """
    try:
        opts, args = getopt.getopt(argv, 'h:a', ['arch'])

        if len(opts) == 0:
            print(usage())
            sys.exit(2)
        else:
            for opt in opts:
                # Making sure only one argument is given when -a or --arch options used
                if (opt[0] == "-a" or opt[0] == "--arch") and len(args) == 1:
                    return args
                else:
                    print(usage())
                    break
    except getopt.GetoptError:
        #Print a message or do something useful
        print(usage())
        sys.exit(2)


def logs(level, message):
    """
    Logging function to aid with ease of logging the errors and processes
    input vars can be a level which is either warning,error, or infor or critical as
    well as a message to tell what one is logging be it a stack from exception
    or so.
    """
    if level is "info":
        # This is not working as expected , thus will come back to it later
        logging.info(message)
    elif level is "warning":
        logging.warning(message)
    elif level is "error":
        logging.error(message)
    elif level is "critical":
        logging.critical(message)
    else:
        logging.error(message)


def main(argv):
    # Tracking logs
    logs("warning","Starting package_statistics tool")
    # Main mirror to use ofr getting our stats resources
    MIRROR = "http://ftp.uk.debian.org/debian/dists/stable/main/"
    args = CLI_argv(argv)
    if not args:
        logs("warning","An issue occurred that inhibits the tool from getting the artitecture value given!")
        sys.exit(2)

    stats = PKG_STATS()
    stats.set_root(MIRROR)
    stats.set_arch(args[0])
    stats.downloader(MIRROR) # Getintial links for compressed sources
    stats.process_compressed_files()
    stats.answers_you_seek()

    logs("warning","Finished processing package_statistics tool")




if __name__ == "__main__":
    main(sys.argv[1:])
