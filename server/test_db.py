#!/usr/bin/python
# coding: utf-8

from db import RecruitInfo, Recruit, Company
from test_base import createDummy, removeDummy

from mongoengine import connect

from unittest import TestCase
import json


class Test_RecruitInfo(TestCase):
    @classmethod
    def setUpClass(cls):
        createDummy()

    @classmethod
    def tearDownClass(cls):
        removeDummy()


    def setUp(self): pass
    def tearDown(self): pass

    
    def test_RecruitInfo(self):
        idx = '2'
        info = RecruitInfo(idx)
        self.assertEqual(info.json, info.obj._data)
        # repr(info) will be the dumpe of json
        self.assertEqual(repr(info), json.dumps(info.obj._data))

        url = 'http://www.saramin.co.kr/zf_user/recruit/recruit-view?idx=2'
        info2 = RecruitInfo(url)
        self.assertEqual(info2.json, info2.obj._data)
        #self.assertEqual(info2.json, {'rating': None, 'full': None, 'idx': u'2', 'url': None, 'company': None, 'summary': None, 'dday': None, 'memo': u'The idx is 2'})

        mjson = {"url": 'http://www.saramin.co.kr/zf_user/recruit/recruit-view?idx=18',
                "rating": '3',
                "memo": "this is memo"}
        
        info3 = RecruitInfo()
        info3.getFromJson(mjson)
        info3.save()
        #self.assertEqual(info3.json, {'rating': '3', 'full': None, 'idx': '18', 'url': 'http://www.saramin.co.kr/zf_user/recruit/recruit-view?idx=18', 'memo': 'this is memo', 'summary': None, 'dday': None, 'company': None})

        # Check the save
        info18 = RecruitInfo('18')
        self.assertEqual(info18.memo, 'this is memo')
        # Fixme: It don't work. infoc will return 'this is memo'.
        info18.memo = "aaa"
        info18.save()
        self.assertEqual(info18.memo, 'aaa')


        infoc = RecruitInfo('18')
        self.assertEqual(infoc.memo, 'aaa')


        mjson2 = {"url": 'http://www.saramin.co.kr/zf_user/recruit/recruit-view?idx=18',
                "rating": '3',
                "memo": "memo2"}

        infoa = RecruitInfo()
        infoa.getFromJson(mjson2)
        infoa.save()

        infoa2 = RecruitInfo('18')
        self.assertEqual(infoa2.memo, 'memo2')

        info2.aac = "aac"
        self.assertEqual(info2.aac, 'aac')

        # getFromObject method
        rec_obj = Recruit.objects(idx='18')[0]
        infoa3 = RecruitInfo()
        infoa3.getFromObject(rec_obj)
        self.assertEqual(infoa2.memo, 'memo2')
        
