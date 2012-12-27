#!/usr/bin/python
# coding: utf-8

import re
import os
import imdb
import Image
from StringIO import StringIO
from subprocess import Popen, PIPE
from datetime import datetime, timedelta

import urllib2, time
try:
    from BeautifulSoup import BeautifulSoup
    MODULE_BEAUTIFULSOUP = True
except ImportError:
    MODULE_BEAUTIFULSOUP = False

from lxml.cssselect import CSSSelector
from lxml.html import parse, fromstring, tostring


from base_webkit import WebkitInterface


class Container(object):
    """

    >>> url = 'http://www.saramin.co.kr/zf_user/recruit/recruit-view?location=ts&idx=13556353'
    >>> cont = Container(url, char_set='euc-kr', webkit=True) #doctest: +SKIP
    >>> cont.save('saramin.html') #doctest: +SKIP
    """
    def __init__(self, url=None, char_set=None, webkit=False):
        self.url = url
        self.char_set = char_set
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
        self._setCharset(fd)

        # TODO: Automatically detect character encoding. We can get the
        # information from http request.
        
        # if chardet.detect(_content)['encoding'] == 'EUC-KR': _content =
        # unicode(_content, 'euc-kr').encode('utf-8')
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
        try:
            content = fd.headers['content-type']
        except KeyError:
            pass

        pattern = re.compile('charset=(.*)')
        search = pattern.search(content)
        if search:
            self.char_set = search.group(1)

    def pretty(self, url=None):
        if url:
            self.get(self.url)
        if not self.source:
            return "We need pretty(url) or do get(url)"
            
        soup = BeautifulSoup(self.source)
        return soup.prettify()

    @classmethod
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




class SaraminContainer(InfoBase):

    '''

    >>> url = 'http://www.saramin.co.kr/zf_user/recruit/recruit-view?location=ts&idx=13556353'
    >>> #url = 'http://www.saramin.co.kr/zf_user/recruit/company-info-view/idx/4251025'
    >>> sac = SaraminContainer(url)
    >>> sac.get() #doctest: +SKIP
    >>> sac.get(path='saramin.html')
    >>> sac.infos #doctest: +SKIP
    {'url': 'http://www.saramin.co.kr/zf_user/recruit/recruit-view?location=ts&idx=13556353', 'idx': '13556353', 'recruit_dday': '-15', 'company_name': u'(\uc8fc)\ud050\uc5e0\uc528', 'company_idx': '4251025'}

    >>> #Fixme: saramin has encoding error with urllib.
    >>> sac2 = SaraminContainer(url, webkit=False) #doctest: +SKIP
    >>> sac2.get() #doctest: +SKIP
    >>> sac2.infos #doctest: +SKIP
    '''
    
    def __init__(self, url, webkit=True):
        url = self._getUrlFromIdx(url)
        self.webkitp = webkit
        super(SaraminContainer, self).__init__(url)
        self.infos = {}
        self.source_company_summary = ''
        self.source_recruit_summary = ''
    
    def _getAll(self):
        self.infos = {}
        p_methods = self.parsingMethods()
        for m in p_methods:
            method = getattr(self, 'get_' + m)
            db = method()
            self.infos[m] = db

    def get(self, path=None):
        if not self.url:
            raise AttributeError("Object has None url")
        if path:
            self.container = Container()
            self.container.char_set = 'euc-kr'
            self.container.fromFile(path)
        else:
            self.container = Container(self.url, char_set='euc-kr', webkit=self.webkitp)
            self.container.get()
        #print len(self.container.source)
        self._setSummaries()
        self._getAll()

    def _getBase(self, selector):
        # sel = CSSSelector(selector)
        # sel_list = sel(element)
        # print tostring(sel_list[0])
        # result.append(sel_list[0].text)
        # return result
        pass

    def _setSummaries(self):
        # cssselctor 'table.smr' returns two elements. First is summary of
        # company, other is summary of recruit.
        sel = CSSSelector('table.smr')
        sel_list = sel(fromstring(self.container.source))
        company_offset = 0
        recruit_offset = 1
        # There is encoding problem with ipython on emacs.
        # self.source_company_summary = tostring(sel_list[company_offset], encoding='utf-8')
        # self.source_recruit_summary = tostring(sel_list[recruit_offset], encoding='utf-8')
        self.source_company_summary = tostring(sel_list[company_offset])
        self.source_recruit_summary = tostring(sel_list[recruit_offset])

    def _get_company_base(self, num, debug=None):
        sel = CSSSelector('tbody tr td')
        sel_list = sel(fromstring(self.source_company_summary))
        if debug: print tostring(sel_list[num], encoding='utf-8')
        return sel_list[num].text

    def _get_recruit_base(self, num, debug=None):
        pass

    def get_title(self):
        return self._get_company_base(1)

    def _get_end(self):
        # TODO: about 상시모집
        pattern = re.compile('<span class="point_01">\(D([0-9\-]+)\)</span>')
        match = pattern.search(self.source_recruit_summary)
        try:
            counter = match.group(1)
            counter_int = int(counter)
            counter_positive_int = abs(counter_int)
            today = datetime.today()
            end = today + timedelta(counter_positive_int)
            return end.strftime('%Y-%m-%dT%H:%M:%S')
            
        except AttributeError:
            return None

    def get_end(self):
        # TODO: about 상시모집
        pattern = re.compile('<span class="point_01">\(D([0-9\-]+)\)</span>')
        match = pattern.search(self.source_recruit_summary)
        try:
            counter = match.group(1)
            counter_int = int(counter)
            counter_positive_int = abs(counter_int)
            today = datetime.today()
            end = today + timedelta(counter_positive_int)
            return end
            
        except AttributeError:
            return None

    def get_start(self):
        # TODO: about 상시모집
        pattern = re.compile('<span class="point_01">\(D([0-9\-]+)\)</span>')
        match = pattern.search(self.source_recruit_summary)
        try:
            counter = match.group(1)
            counter_int = int(counter)
            counter_positive_int = abs(counter_int)
            today = datetime.today()
            end = today + timedelta(counter_positive_int)
            return end
            
        except AttributeError:
            return None


    def get_idx(self):
        try:
            pattern = re.compile('idx=([0-9]+)')
            match = pattern.search(self.url)
            result = match.group(1)
        except:
            result = None
        return result

    def get_url(self):
        return self.url

    def get_recruit_summary(self):
        return self.source_recruit_summary

    def get_company_idx(self):
        sel = CSSSelector('div.company-tools a')
        sel_list = sel(fromstring(self.container.source))
        url = sel_list[0].get('href')

        try:
            pattern = re.compile('idx/([0-9]+)')
            match = pattern.search(url)
            result = match.group(1)
        except:
            result = None
        return result


    def __get_test1(self):
        # It will returns two element. First is summary of company, other is
        # summary of recruit
        sel = CSSSelector('table.smr')
        sel_list = sel(fromstring(self.container.source))
        print sel_list
        namen = 1
        for a in sel_list:
            print tostring(a, encoding='utf-8')
            name = 'aaa' + str(namen) + '.html'
            cont = Container()
            cont.source = tostring(a, encoding='utf-8')
            cont.pretty()
            cont.save(name)
            namen += 1
        return 'aaa'

    def __get_test2(self):
        sel = CSSSelector('span#recruit-company-title')
        sel_list = sel
        sel = CSSSelector('td.gul12_44')
        sel_list = sel(fromstring(self.container.source))
        # print sel_list
        # for a in sel_list:
        #     bb = a.text
        #     if bb == None:
        #         print a.xpath('string()')
        #     else:
        #         print bb
        #         print a.getchildren()
        #     print "----", tostring(a)
        for a in sel_list:
            bb = a.text
            #print bb
            t = re.compile(u'.*(회사명).*')
            try:
                m = t.search(bb)
                tok = m.group(0)
                print 'aaa', tok

                print a.getchildren()
            except:
                pass

        return 'aaa'

    # def _has(self, source, regexp):
    #     token = re.compile(regexp)
        

    # def get_company_sector(self):
    #     pass

    # def get_companySales(self):
    #     pass

    # def get_companyAssets(self):
    #     pass

    # def get_companyPeopleNumber(self):
    #     pass

    # def get_companyUrl(self):
    #     pass

    # def get_companyLocation(self):
    #     pass

    # def get_pageUrl(self):
    #     pass


    def _getUrlFromIdx(self, idx_or_url):
        if idx_or_url[:4] == 'http':
            return idx_or_url
        else:
            return 'http://www.saramin.co.kr/zf_user/recruit/recruit-view?location=ts&idx=%s' % idx_or_url
