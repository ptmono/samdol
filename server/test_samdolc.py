#!/usr/bin/python
# coding: utf-8

import config
from db import RecruitInfo, Recruit, Company

from mongoengine import connect
from unittest import TestCase

import urllib


class Test_Samdolc(TestCase):
    @classmethod
    def setUpClass(cls):
        connect(config.db_name_test)

    @classmethod
    def tearDownClass(cls):
        Recruit.drop_collection()
        Company.drop_collection()

    def setUp(self):
        pass
    def tearDown(self):
        pass

    
    # def test_posting(self):
    #     url = 'http://localhost:8222/post?%s'
    #     params = urllib.urlencode({"url": "http://www.saramin.co.kr/zf_user/recruit/recruit-view?idx=13782034", "rating": "3", "memo": " - test\n - test 2"})
        
    #     f = urllib.urlopen(url % params)

    #     idx = '13782034'
    #     info = Recruit.objects(idx=idx)[0]
    #     self.assertEqual(info.idx, idx)


class Test_SamdolcAction(TestCase):
    @classmethod
    def setUpClass(cls):
        connect(config.db_name_test)

    @classmethod
    def tearDownClass(cls):
        Recruit.drop_collection()
        Company.drop_collection()

    def setUp(self):
        pass
    def tearDown(self):
        pass
    
