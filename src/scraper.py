import requests
import lxml.html
import re
from bs4 import BeautifulSoup
import urllib3

class WebScraper:
    def __init__(self, **kwargs) -> None:
        self.loadedPage = None if 'url' not in kwargs else kwargs['url']
        self.loadedData = []
        self.parser = None if 'parser' not in kwargs else kwargs['parser']
        self.accepter = None if 'accepter' not in kwargs else kwargs['accepter']
        self.interpreter = None if 'interpreter' not in kwargs else kwargs['interpreter']
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
            if self.parser is not None: self.collectedData = self.parser(self.collectedData, self.loadedData)
            if self.accepter is not None:
                if self.accepter(self.collectedData): break
                tries -= 1
            else: break
        if self.interpreter is not None: 
            return self.interpreter(self.collectedData)
        return self.collectedData
