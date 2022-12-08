import requests
import lxml.html
import re
from bs4 import BeautifulSoup
import urllib3
import json

'''
Breakdown:
    - Load site data
    - Parse site data based on needs criteria
    - Determine if site data loaded is valid enough based on acceptance criteria
    - If data doesn't meet acceptance criteria try again until 'tries' are exhausted
'''

class WebScraper:
    def __init__(self, **kwargs) -> None:
        self.loadedPage = None if 'url' not in kwargs else kwargs['url']
        self.loadedData = []
        self.parser = None if 'parser' not in kwargs else kwargs['parser']
        self.accepter = None if 'accepter' not in kwargs else kwargs['accepter']
        self.collectedData = {}

    def scrapePage(self, url=None, tries=1):
        if url is None: url = self.loadedPage
        else: self.loadedPage = url
        self.collectedData = {}
        while tries > 0:
            try: html = requests.get(url, timeout=1)
            except: return None, None
            doc = lxml.html.fromstring(html.content)
            div = doc.xpath('.//div[contains(@class, "p-")]')
            if len(div) < 1:
                http = urllib3.PoolManager()
                div = BeautifulSoup(html.raw.data).get_text()
                return None, None
            self.loadedData = re.split(r'<|>', str(lxml.html.tostring(div[0])))
            self.collectedData = self.parser(self.collectedData, self.loadedData)
            if self.accepter(self.collectedData): return self.collectedData
            tries -= 1
        return self.collectedData

def loadDataFromJson(loadFile):
    fileJson = {}
    with open(loadFile) as json_file:
        fileJson = json.load(json_file)
    return fileJson

def accepter(data) -> bool:
    pass

def parser(data, stringList) -> dict:
    pass

def interpreter():
    pass
