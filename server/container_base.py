#!/usr/bin/python
# coding: utf-8

import re
import os
from subprocess import Popen, PIPE

import urllib2, time
try:
    from BeautifulSoup import BeautifulSoup
    MODULE_BEAUTIFULSOUP = True
except ImportError:
    MODULE_BEAUTIFULSOUP = False

from lxml.cssselect import CSSSelector
from lxml.html import fromstring

class Container(object):
    """

    >>> url = 'http://www.saramin.co.kr/zf_user/recruit/recruit-view?location=ts&idx=13556353'
    >>> cont = Container(url, char_set=None, webkit=False) #doctest: +SKIP
    >>> cont.save('saramin2.html') #doctest: +SKIP
    """
    def __init__(self, url=None, char_set=None, auto_char_set=None, webkit=False):
        self.url = url
        self.char_set = char_set
        self.auto_char_set = auto_char_set
        self.webkit = webkit
        
        self.d = urllib2
        self.source = None
        if url:
            self.get()

    def get(self, url=None):
        if url:
            self.url = url

        if self.webkit:
            self._getWithWebkit()
        else:
            self._getWithUrllib2()

    def _getWithUrllib2(self):
        fd = self._downAUrl(self.url)
        self.source = fd.read()
        # Detect charset form content
        if self.auto_char_set: self._setCharset(fd)


        if self.char_set:
            try:
                self.source = self.source.decode(self.char_set)
            except LookupError:
                pass

    def _getWithWebkit(self):
        # webkit = WebkitInterface()
        # webkit.getSource(self.url, self.char_set)
        # self.source = webkit.source

        path_base = os.path.abspath(__file__)

        path = os.path.dirname(path_base) + "/_tmp_uuwebkit.html"

        ab_base_webkit = os.path.dirname(path_base) + "/base_webkit.py"

        Popen(["python", ab_base_webkit, self.url, str(self.char_set), path],
              stdout=PIPE).communicate()[0]
        fd = open(path, 'r')
        self.source = fd.read()
        fd.close()

    def _setCharset(self, fd):
        # if chardet.detect(_content)['encoding'] == 'EUC-KR': _content =
        # unicode(_content, 'euc-kr').encode('utf-8')
        try:
            content = fd.headers['content-type']
        except KeyError:
            pass

        pattern = re.compile('charset=(.*)')
        search = pattern.search(content)
        if search:
            self.char_set = search.group(1)

    # def pretty(self, url=None):
    #     if url:
    #         self.get(self.url)
    #     if not self.source:
    #         return "We need pretty(url) or do get(url)"

        
    #     soup = BeautifulSoup(self.source)
    #     return soup.prettify()

    def save(self, path):
        # fd = open(path, 'w')
        # fd.write(self._downAUrl(self.url).read())
        # fd.close()
        fd = open(path, 'w')
        fd.write(self.source)
        fd.close()
    
    def _downAUrl(self, url):
        """There was urllib2.URLError 110. 110 is time out error. So we
        try 5 times more."""
        i = 0
        while i != 5:
            try:
                dn = self.d.urlopen(url)
                return dn
            except:
                time.sleep(1)
                i = i + 1
        raise 'urllib2.URLError', 'I think server is blocking you'

    def fromFile(self, path):
        fd = open(path, 'r')
        self.source = fd.read()
        if self.char_set:
            self.source = self.source.decode(self.char_set)
        fd.close()


class InfoBase(object):
    """
    The class return the list of line infomation some like
    [dictionary1,dictionary2 ...]
    where dictionary is like
    {'votes': '3', 'hits': '17', 'titles': 'Metallica RockInRio Brazil 26-09-2011', 'numbers': '17804'}

    From above dictionary the infomation is 'votes', 'hits', 'titles',
    'numbers'. We have to parse the information. We will separately parse
    each information on a page as list. The class merge the information as
    the list of dictionary.

    To get the list of 'titles' you have to create 'getTitles' method that
    returns the list of titles on the page. Write the methods for 'votes',
    'hits', 'numbers' as 'getVotes', 'getHits', 'getNumbers'. It also
    returns the list of that information.
    
    >>> info = InfoBase()
    >>> info.infos = [{'votes': '3', 'hits': '17', 'titles': 'Metallica RockInRio Brazil 26-09-2011', 'numbers': '17804', 'links': '../bbs/board.php?bo_table=movie_t&wr_id=1300054'}]

    """
    def __init__(self, url=None):
        self.url = url
        self.infos = []
        self.container = None
        self.iter_counter = 0

    def __iter__(self):
        return self

    def next(self):
        if self.iter_counter is len(self):
            self.iter_counter = 0
            raise StopIteration
        result = self.infos[self.iter_counter]
        self.iter_counter +=1
        return result
        
    def __len__(self):
        return len(self.infos)

    def __getitem__(self, key):
        return self.infos[key]

    def reverse(self):
        self.infos.reverse()

    def get(self):
        if not self.url:
            raise AttributeError("Object has None url")
        self.container = Container(self.url)
        self._getAll()

    def parsingMethods(self):
        result = []
        pattern = re.compile('get_([A-z_]+)')
        for a in dir(self):
            match = pattern.match(a)
            if match:
                element = match.group(1).lower()
                result.append(element)
        return result

    def _getAll(self):
        results = []
        self.infos = []
        p_methods = self.parsingMethods()
        methods_length = len(p_methods)
        for m in p_methods:
            method = getattr(self, 'get_' + m)
            db = method()
            results.append(db)

        method_length = len(results[0])
        for counter in range(method_length):
            element = {}
            for num in range(methods_length):
                element[p_methods[num]] = results[num][counter]
            self.infos.append(element)
        self.infos.reverse()

        
    def _getBase(self, selector):
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(self.container.source))
        #result = image_names = [name.get('value') for name in sel_list]
        return [name.text for name in sel_list]

    def _getBaseGetAttr(self, selector, attr):
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(self.container.source))
        #result = image_names = [name.get('value') for name in sel_list]
        return [name.get(attr) for name in sel_list]




