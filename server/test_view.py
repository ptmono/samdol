#!/usr/bin/python
# coding: utf-8

from unittest import TestCase
from datetime import datetime, timedelta
import json

import config
from db import RecruitInfo, Recruit, Company
from test_base import createDummy, removeDummy

from view import recruits, _recruits, documents2jsondump, ViewRecruits, documents2FullcalendarObject

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
    
    def _recruits(self):
        today = datetime.today()
        yesterday = today + timedelta(-1)
        recs = Recruit.objects
        recs = Recruit.objects(end__gt = yesterday)
        
        #self.assertEqual(recruits(), 0)


    def viewRecruits(self):
        recruits = ViewRecruits()        
        #self.assertEqual(recruits.getContent(), 0)
        
    def documents2jsondump(self):
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

    def document2fullcalendar(self):
        today = datetime.today()

        rec = Recruit()
        rec.idx = '8888'
        rec.url = 'http://google.com'
        rec.title = u'몰라'
        rec.end = datetime.today()
        rec.save()

        rec_info = RecruitInfo('8888')
        #self.assertEqual(0,1)



class RatingColors:
    RED = 5        


class Test_Fullcalendar_objects(TestCase):
    @classmethod
    def setUpClass(cls):
        pass
    @classmethod
    def tearDownClass(cls):
        pass
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_add_color(self):
        colors = {'1': '#D8D8D8', '2': '#959595', '3': '#0009FF', '4': '#970000', '5': '#FF0000'}
        new_recs = []
        recs = _recruits()
        for rec in recs:
            try:
                color = colors[rec.rating]
            except:
                color = '3'
            rec.color = color
            new_recs.append(rec)

        #print documents2jsondump(new_recs)
        print documents2FullcalendarObject([new_recs[1]])
            
        self.assertEqual(0, 1)

        
