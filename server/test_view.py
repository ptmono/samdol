#!/usr/bin/python
# coding: utf-8

from unittest import TestCase
from datetime import datetime, timedelta
import json

import config
from db import RecruitInfo, Recruit, Company
from test_base import createDummy, removeDummy

from view import recruits, documents2jsondump



class Test_Calendar(TestCase):
    @classmethod
    def setUpClass(cls):
        createDummy()

    @classmethod
    def tearDownClass(cls):
        removeDummy()

    def setUp(self):
        pass
    def tearDown(self):
        pass
    
    def test_recruits(self):
        today = datetime.today()
        yesterday = today + timedelta(-1)
        recs = Recruit.objects
        recs = Recruit.objects(end__gt = yesterday)
        
        #self.assertEqual(recruits(), 0)

    def test_documents2jsondump(self):
        today = datetime.today()
        yesterday = today + timedelta(-1)
        recs = Recruit.objects
        recs = Recruit.objects(end__gt = yesterday)

        result = []
        rec_temp = None
        for rec in recs:
            rec_temp = RecruitInfo()
            rec_temp.getFromObject(rec)
            result.append(rec_temp._repr())

        self.assertEqual(documents2jsondump(recs), json.dumps(result))

    def test_document2fullcalendar(self):
        today = datetime.today()

        rec = Recruit()
        rec.idx = '8888'
        rec.url = 'http://google.com'
        rec.title = u'몰라'
        rec.end = datetime.today()
        rec.save()

        rec_info = RecruitInfo('8888')
        #self.assertEqual(0,1)
