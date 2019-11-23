import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import argparse
import urllib.request
from urllib import robotparser
import time
from urllib import parse
from urllib.parse import urlparse
import os
from os import path

class Crawler:
    def __init__(self):
        self.all_anchors = ""
        self.upper_bound = 0
        self.url = 'https://www.concordia.ca'
        self.nextPage = ""
        self.robottxt = ""
        self.nextUrl = ""
        self.soup = ""
        self.title = ""
        self.content = ""

    def robotExclusion(self):
        parser = robotparser.RobotFileParser()
        parser.set_url(parse.urljoin(self.url, '/robots.txt'))
        parser.read()
        self.robottxt = parser.sitemaps

    def setUpperbound(self, arg):
        self.upper_bound = arg.max

    """
    Get all anchors from /research.html
    """
    def get_anchors(self):
        url = self.url + '/research.html'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        self.soup = soup
        self.all_anchors = soup.findAll('a')


    """
    Loops through all anchors href links
    ex: concordia.ca/about.html, concordia.ca/...
    """
    def loop_pages(self):
        counter = 0
        for i in range(len(self.all_anchors)):
            if(counter <= self.upper_bound + 1):
                anchor = self.all_anchors[i]
                flag = False
                try: 
                    href = anchor['href'] 
                    nextUrl = self.url + href
                    self.nextUrl = nextUrl
                    response_get = requests.get(nextUrl)
                    self.nextPage = response_get
                    self.extractPage()
                    time.sleep(1)
                except:
                    a=1
            counter +=1
    def extractPage(self):
        sub_titles = urlparse(self.nextUrl).path.split('.')[0].split('/')
        title = '_'.join(sub_titles)[1:]
        self.title = title
        tags = ['p', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'th', 'td']
        content = ''
        for tag in tags:
            content += '\n' + '\n'.join([txt.text for txt in self.soup.find(id='content-main').find_all(tag)])
        self.content = content
        self.writePagesToFiles()

    def writePagesToFiles(self):
        with open(os.getcwd() + '/Pages/' + self.title + '.txt', 'w') as file:
            data = {'title': self.title, 'url': self.nextUrl , 'content': self.content}
            file.write(str(data))
        

parser = argparse.ArgumentParser()
parser.add_argument('max', type=int, action="store", help="Choose upperbound value for number of pages to navigate")
args = parser.parse_args()

c = Crawler()
c.robotExclusion()
c.setUpperbound(args)
c.get_anchors()
c.loop_pages()
