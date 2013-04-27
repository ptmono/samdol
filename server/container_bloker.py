#!/usr/bin/python
# coding: utf-8

import re

from dexceptions import NoContainerException
from container_base import InfoBase

# TODO: Easy way? to automatically add the containers.
from container_saramin import SaraminContainer
from container_worknet import WorknetContainer

class ContainerBloker(object):
    '''
    >>> url1 = 'http://www.saramin.co.kr/zf_user/recruit/recruit-view?location=ts&idx=13556353'
    >>> url2 = 'http://www.work.go.kr/empInfo/empInfoSrch/detail/empDetailAuthView.do?callPage=detail&wantedAuthNo=K120231301240001&rtnUrl=/empInfo/empInfoSrch/list/dtlEmpSrchList.do?len=0&tot=0&lastIndex=1&firstIndex=1&pageSize=10&recordCountPerPage=10&rowNo=0&softMatchingPossibleYn=N&charSet=EUC-KR&startPos=0&collectionName=tb_workinfo&softMatchingMinRate=+66&softMatchingMaxRate=100&certifiYn=N&preferentialYn=N&siteClcd=all&empTpGbcd=1&onlyTitleSrchYn=N&onlyContentSrchYn=N&resultCnt=10&sortOrderBy=DESC&sortField=DATE&pageIndex=1&pageUnit=10'
    >>> url3 = 'http://ppf.je.ro'

    >>> blocker = ContainerBloker(url3) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    NoContainerException: http://ppf.je.ro

    >>> bloker = ContainerBloker(url1)
    >>> bloker.get().infos #doctest: +SKIP
    # This is the recruit ended on worknet.
    >>> bloker.setContainer(url2)
    >>> bloker.get().infos #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    XMLSyntaxError: line 2958: Invalid char in CDATA 0x0

    >>> # Test for saramin
    >>> blocker = ContainerBloker(url1)
    >>> blocker.idx()
    '13556353'
    
    >>> # Test for worknet
    >>> url4 = 'http://www.work.go.kr/empInfo/empInfoSrch/detail/retrivePriEmpDtlView.do?iorgGbcd=CSI&callPage=detail&wantedAuthNo=14386788&rtnUrl=/empInfo/empInfoSrch/list/dtlEmpSrchList.do?len=0&tot=0&region=26000&lastIndex=1&firstIndex=1&pageSize=10&recordCountPerPage=10&rowNo=0&softMatchingPossibleYn=Y&charSet=EUC-KR&startPos=0&collectionName=tb_workinfo&softMatchingMinRate=66&softMatchingMaxRate=100&workRegion=26000*%EB%B6%80%EC%82%B0&occupation=13*IT%C2%B7%EC%A0%95%EB%B3%B4%ED%86%B5%EC%8B%A0%C2%B7%EC%9B%B9*null&certifiYn=N&preferentialYn=N&siteClcd=all&empTpGbcd=1&onlyTitleSrchYn=N&onlyContentSrchYn=N&resultCnt=10&sortOrderBy=DESC&sortField=DATE&pageIndex=2&pageUnit=10'
    >>> bloker = ContainerBloker(url4)
    >>> bloker.get().infos #doctest: +SKIP
    '''
    
    def __init__(self, url):
        self.url = url
        self.containers = InfoBase.__subclasses__()
        self.container = self.getContainer(url)

    def get(self):
        container = self.container(self.url)
        return container.get()

    def idx(self, url=None):
        obj = self.container(self.url)
        return obj.get_idx()

    def getContainer(self, url):
        for container in self.containers:
            pattern = re.compile(container.site)
            search = pattern.search(url)
            if search:
                return container
        raise NoContainerException(url)

    def setContainer(self, url):
        self.container = self.getContainer(url)



