#!/usr/bin/python
# coding: utf-8

import re
from datetime import datetime, timedelta

from lxml.cssselect import CSSSelector
from lxml.html import fromstring, tostring

import config
from container_base import Container, InfoBase

class SaraminContainer(InfoBase):

    '''

    >>> url = 'http://www.saramin.co.kr/zf_user/recruit/recruit-view?location=ts&idx=13556353'
    >>> #url = 'http://www.saramin.co.kr/zf_user/recruit/company-info-view/idx/4251025'
    >>> sac = SaraminContainer(url)
    >>> sac.get() #doctest: +SKIP
    >>> sac.get(path='etc/saramin.html')
    >>> sac.infos #doctest: +SKIP
    {'url': 'http://www.saramin.co.kr/zf_user/recruit/recruit-view?location=ts&idx=13556353', 'idx': '13556353', 'recruit_dday': '-15', 'company_name': u'(\uc8fc)\ud050\uc5e0\uc528', 'company_idx': '4251025'}

    >>> #Fixme: saramin has encoding error with urllib.
    >>> sac2 = SaraminContainer(url, webkit=False)
    >>> sac2.get()
    >>> #sac2.infos

    ### === get_idx, url type recldx/14053736
    ### __________________________________________________________
    >>> url = "http://www.saramin.co.kr/zf_user/special-recruit/list/bcode/51/code/E1/search_area/2/page/1/pageCount/80/CategoryViewFlag/1/recIdx/14053736"
    >>> url_sac = SaraminContainer(url, webkit=False)
    >>> url_sac.get_idx()
    '14053736'
    '''
    site = "saramin.co.kr"
    
    def __init__(self, url_or_idx, webkit=False):
        url = self._getUrlFromIdx(url_or_idx)
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
            self.container.fromFile(path)
        else:
            self.container = Container(self.url, webkit=self.webkitp)
            self.container.get()
        #print len(self.container.source)
        self._setSummaries()
        self._getAll()
        return self

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
        try:
            self.source_company_summary = tostring(sel_list[company_offset])
            self.source_recruit_summary = tostring(sel_list[recruit_offset])
        except IndexError:
            # This case only recruit_summary is exist
            self.source_company_summary = ""
            self.source_recruit_summary = tostring(sel_list[0])

    def _get_company_base(self, num, debug=None):
        sel = CSSSelector('tbody tr td')
        try:
            sel_list = sel(fromstring(self.source_company_summary))
            if debug: print tostring(sel_list[num], encoding='utf-8')
            return sel_list[num].text
        except:
            #FIXME: issue 1301161926. Create unit test.
            return "NoCompanyInfo"
            

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
            pattern = re.compile('(idx=|recIdx/|idx/)([0-9]+)')
            match = pattern.search(self.url)
            result = match.group(2)
        except Exception, err:
            config.logger.error(repr(err))
            result = None
        return result

    def get_url(self):
        return self.url

    def get_recruit_summary(self):
        return self.source_recruit_summary

    def get_company_idx(self):
        sel = CSSSelector('div.company-tools a')
        sel_list = sel(fromstring(self.container.source))

        try:
            # There is no company summary
            url = sel_list[0].get('href')
        except IndexError:
            return None

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
            #cont.pretty()
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
