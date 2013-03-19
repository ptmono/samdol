#!/usr/bin/python
# coding: utf-8

import config
from db import Recruit, Company
from mongoengine import connect

from datetime import datetime, timedelta
from unittest import TestCase

def createDummy():

    connect(config.db_name_test)

    today = datetime.today()

    company1 = Company()
    company1.idx = '93920'
    company1.name = '달수네'
    company1.save()

    company2 = Company()
    company2.idx = '99910'
    company2.name = '말수네'
    company2.save()

    recruit1 = Recruit()
    recruit1.idx = '1'
    recruit1.memo = 'The idx is 1'
    recruit1.end = today + timedelta(-3)
    recruit1.save()

    recruit2 = Recruit()
    recruit2.idx = '2'
    recruit2.memo = 'The idx is 2'
    recruit2.end = today + timedelta(0)
    recruit2.save()

    recruit3 = Recruit()
    recruit3.idx = '3'
    recruit3.memo = 'The idx is 3'
    recruit3.end = today + timedelta(3)
    recruit3.save()

    recruit4 = Recruit()
    recruit4.idx = '4'
    recruit4.title = "permanent recruit"
    recruit4.memo = 'The idx is 4'
    recruit4.end = None
    recruit4.save()

    
def removeDummy():

    Recruit.drop_collection()
    Company.drop_collection()


class Test_createDummy(TestCase):
    @classmethod
    def setUpClass(cls):
        createDummy()

    @classmethod
    def tearDownClass(cls):
        removeDummy()

    def test_base(self):
        recruits = Recruit.objects
        for recruit in recruits:
            print recruit.end
            print recruit.memo
        #self.assertEqual(recruits, 0)
