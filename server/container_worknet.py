#!/usr/bin/python
# coding: utf-8

import re
from datetime import datetime, timedelta

from lxml.cssselect import CSSSelector
from lxml.html import fromstring, tostring

import config
from container_base import Container, InfoBase


class WorknetContainer(InfoBase):
    '''
    >>> # 
    >>> url = 'http://www.work.go.kr/empInfo/empInfoSrch/detail/empDetailAuthView.do?callPage=detail&wantedAuthNo=K120231301240001&rtnUrl=/empInfo/empInfoSrch/list/dtlEmpSrchList.do?len=0&tot=0&lastIndex=1&firstIndex=1&pageSize=10&recordCountPerPage=10&rowNo=0&softMatchingPossibleYn=N&charSet=EUC-KR&startPos=0&collectionName=tb_workinfo&softMatchingMinRate=+66&softMatchingMaxRate=100&certifiYn=N&preferentialYn=N&siteClcd=all&empTpGbcd=1&onlyTitleSrchYn=N&onlyContentSrchYn=N&resultCnt=10&sortOrderBy=DESC&sortField=DATE&pageIndex=1&pageUnit=10'
    >>> wc = WorknetContainer(url)
    >>> wc.get() #doctest: +SKIP
    >>> wc.get(path='etc/worknet.html') #doctest: +ELLIPSIS
    <con...>
    >>> wc.get_idx()
    'K120231301240001'
    >>> wc.infos #doctest: +SKIP
    >>> wc.infos['end']
    datetime.datetime(2013, 2, 20, 0, 0)
    >>> wc.infos['start']
    datetime.datetime(2013, 1, 23, 0, 0)
    >>> wc.infos['company_name']
    'KOMEC'

    >>> ### other cases
    >>> # To get end day, there is few format.
    >>> wc = WorknetContainer(url)

    >>> #worknet2.html is for "D--1"
    >>> wc.get(path='etc/worknet2.html') #doctest: +ELLIPSIS
    <con...>
    >>> wc.infos['end'] #doctest: +ELLIPSIS
    datetime.datetime(2013, 2, 9...)
    >>> wc.infos['company_name'] == u'주식회사 지엠에스앤디'
    True

    >>> #worknet3.html is for "D-15"
    >>> wc.get(path='etc/worknet3.html') #doctest: +ELLIPSIS
    <con...>
    >>> wc.infos['end'] #doctest: +ELLIPSIS
    datetime.datetime(2013, 2, 23, ...)
    >>> wc.infos['company_name'] == u'링크정보시스템(주)'
    True

    >>> #worknet4.html is for 상시모집
    >>> wc.get(path='etc/worknet4.html') #doctest: +ELLIPSIS
    <con...>
    >>> wc.infos['end']
    >>> wc.infos['company_name'] == u'㈜제이디원'
    True
    >>> # other "채용시까지"
    
    '''
    site = "work.go.kr"
    base_url = 'http://www.work.go.kr/empInfo/empInfoSrch/detail/empDetailAuthView.do?callPage=detail&wantedAuthNo=%s'
    def __init__(self, url_or_idx, webkit=False):
        self.url = self._getUrlFromIdx(url_or_idx)
        self.webkitp = webkit
        super(WorknetContainer, self).__init__(self.url)
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
        self._setSummaries()
        self._getAll()
        return self

    def _setSummaries(self):
        # recruit info. work type, days
        sel = CSSSelector('table.info_list')
        sel_list = sel(fromstring(self.container.source))
        try:
            self.source_recruit_summary = tostring(sel_list[0], encoding='utf-8')
        except IndexError:
            self.source_recruit_summary = ''

        # company info
        sel = CSSSelector('div.coinfo')
        sel_list = sel(fromstring(self.container.source))
        try:
            self.source_company_summary = tostring(sel_list[0], encoding='utf-8')
        except IndexError:
            self.source_company_summary = ''

    def get_idx(self):
        try:
            pattern = re.compile('wantedAuthNo=([^&]+)')
            match = pattern.search(self.url)
            result = match.group(1)
        except Exception, err:
            config.logger.error(repr(err))
            result = None
        return result

    def get_title(self):
        sel = CSSSelector('div.h3 h3')
        sel_list = sel(fromstring(self.container.source))
        return sel_list[0].text

    def get_start(self):
        pattern = re.compile('접수시작일[^2]+([0-9]+)년 ([0-9]+)월 ([0-9]+)일')
        match = pattern.search(self.source_recruit_summary)
        try:
            year = match.group(1)
            month = match.group(2)
            day = match.group(3)

            date = datetime(year=int(year), month=int(month), day=int(day))
            return date
        except AttributeError:
            return None

    def get_end(self):
        pattern = re.compile('접수마감일[^2t]+([0-9]+)년 ([0-9]+)월 ([0-9]+)일')
        match = pattern.search(self.source_recruit_summary)
        try:
            year = match.group(1)
            month = match.group(2)
            day = match.group(3)

            end = datetime(year=int(year), month=int(month), day=int(day))
            return end
        except AttributeError:
            pass

        try:
            # Type2 and type3. It will be D--1 or D-[0-9]+
            pattern = re.compile('<span class="due">[^D]+D-+([0-9]+)')
            match = pattern.search(self.container.source)

            counter = match.group(1)
            counter_int = int(counter)
            today = datetime.today()
            end = today + timedelta(counter_int)
            return end
        except AttributeError:
            pass

        try:
            #채용시까지 or 접수마감유형 : 상시
            pattern = re.compile('(채용시까지|접수마감유형 : 상시)')
            match = pattern.search(self.container.source)
            if match:
                return None
            else:
                raise AttributeError
        except AttributeError:
            config.logger.error("We couldn't parse end day, %s" % self.url)
            return None
            
    def get_company_name(self):
        sel = CSSSelector('td')
        sel_list = sel(fromstring(self.source_company_summary))
        result = sel_list[0].text
        result = result.strip()
        if result == '':
            sel = CSSSelector('td strong')
            sel_list = sel(fromstring(self.source_company_summary))
            result = sel_list[0].text
            result = result.strip()            
        return result

    def get_url(self):
        return self.url

    def get_recruit_summary(self):
        return self.source_recruit_summary

    def get_company_summary(self):
        return self.source_company_summary

    def _getUrlFromIdx(self, idx_or_url):
        if idx_or_url[:4] == 'http':
            return idx_or_url
        else:
            return self.base_url % idx_or_url




