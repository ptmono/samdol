#!/usr/bin/python
# coding: utf-8

import config

from datetime import datetime, timedelta
import json
import re

from mongoengine import *
from parser import SaraminContainer

## worknet
# http://www.work.go.kr/empInfo/empInfoSrch/detail/empDetailAuthView.do?callPage=detail&wantedAuthNo=K151341212120003


class Company(Document):
    name = StringField(max_length=120)
    saramin_idx = DecimalField()
    idx = StringField(primary_key=True)

class Comment(EmbeddedDocument):
    content = StringField()

class Tag(EmbeddedDocument):
    content = StringField()

class Recruit(Document):
    '''
    >>> rec = Recruit()
    >>> rec.endFromCount(3) #doctest: +SKIP
    '2012-12-25T14:12:04'
    '''
    idx = StringField(primary_key=True)
    #dday = StringField()
    start = DateTimeField()
    end = DateTimeField() # It is more convenient to use as string. dday
    url = StringField()
    memo = StringField()
    rating = StringField(max_length=10)
    #company = ReferenceField(Company, dbref=True)
    company_idx = StringField()
    title = StringField()       # company name
    # It has problem with http request. $.getJSON does not read "comments"
    # = []
    # comments = ListField(EmbeddedDocumentField(Comment))
    recruit_summary = StringField()
    full = StringField()

    def endFromCount(self, count):
        if count > 0:
            count = abs(count)
            today = datetime.today()
            end = today + timedelta(count)
            self.end = end.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            self.end = None

class RecruitBase(object):
    '''

    >>> rec = RecruitBase()
    >>> rec._changed_keys
    ['_changed_keys']
    >>> rec.aa = 'bb' 
    >>> rec._changed_keys
    ['_changed_keys', 'aa']

    >>> rec2 = RecruitBase()
    >>> rec2._changed_keys
    ['_changed_keys']

    '''

    #_changed_keys = []
    def __init__(self):
        connect(config.db_name)
        self.obj = None
        self._changed_keys = []

    def __repr__(self):
        return repr(self.json)

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        # __setattr__ is fast than __init__.
        if hasattr(self, "_changed_keys"):
            self._mark_as_changed(key)

    def _mark_as_changed(self, key):
        self._changed_keys.append(key)
    

    @property
    def json(self):
        return self.obj._data

    @json.setter
    def json(self, value):
        self.obj._data = value


class RecruitInfo(RecruitBase):
    def __init__(self, idx_or_url=None):
        super(RecruitInfo, self).__init__()
        self.idx = self._getIdxFromUrl(idx_or_url)
        if self.idx:
            self.get(self.idx)

    def __repr__(self):
        '''
        To use the info for http, juse use repr().
        '''
        result = self._repr()
        return json.dumps(result)

    def _repr(self):
        result = {}
        try:
            # datetime value is not JSON serializable. See more
            # http://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
            result_json = self.json
            if result_json['end']:     # Can be null
                datetime_string = result_json['end'].strftime('%Y-%m-%dT%H:%M:%S')
                result_json['start'] = datetime_string
                result_json['end'] = datetime_string

                result_json['allDay'] = True
            result = result_json

        except AttributeError:
            # There is no self.json. It means that there is no self.obj
            pass
        return result

    def __str__(self):
        return self.__repr__()


    def get(self, idx_or_url):
        self.idx = self._getIdxFromUrl(idx_or_url)
        try:
            self.obj = Recruit.objects(idx=self.idx)[0]
            self.json = self.obj._data
            self.__dict__.update(self.obj._data)
        except IndexError:
            # There is no exist collection
            self.obj = None

    def getFromJson(self, struc):
        try:
            self.idx = struc['idx']
        except KeyError:
            self.idx = self._getIdxFromUrl(struc['url'])
            # no idx in struc
            struc['idx'] = self.idx
        except:
            raise KeyError("struc does not has idx or url key.")

        # # We have to convert rating to int
        # struc['rating'] = int(struc['rating'])
        try:
            self.obj = Recruit.objects(idx=self.idx)[0]
            # We have to mark the change to apprise for mongoengine.
            for key in struc:
                if key != 'idx':
                    self._mark_as_changed(key)
        except IndexError:
            # There is no collection
            self.obj = Recruit()

        self.obj._data.update(struc)
        self.__update_dict()

    def __update_dict(self):
        self.__dict__.update(self.obj._data)

    def getFromObject(self, obj):
        self.obj = obj
        self.__update_dict()

    @classmethod
    def isNew(self, idx_or_url):
        idx = self._getIdxFromUrl(idx_or_url)

        try:
            Recruit.objects(idx=idx)[0]
        except IndexError:
            return True
        return False

    def setIdx(self, idx_or_url):
        self.idx = self._getIdxFromUrl(idx_or_url)

    def save(self):
        # mongoengine uses BaseDocument._deleta() to detect the change of
        # a document. mongoengine just use Document._data to update a
        # document. It means mongoengine doesn't know the change of a
        # document when you have modified Document._data.

        # We can mark the change with Document._mark_as_changed(key).
        # Or we can manually update with collection.update. For instance

        # collection = self.obj.__class__.objects._collection
        # doc = self.obj.to_mongo()
        # object_id = doc['_id']
        # select_dict = {'_id': object_id}
        # collection.update(select_dict, {"$set": {'rating': u'10'} }, False, True}
        
        # See more Document.save() on mongoengine.
        for key in self._changed_keys:
            if key is 'idx': continue
            if key in self.obj._data:
                # Notify change
                self.obj._mark_as_changed(key)
                # Change the change to save
                self.obj._data[key] = self.__dict__[key]
        result = self.obj.save()
        self._changed_keys = []
        return result


    @classmethod
    def _getIdxFromUrl(self, idx_or_url):
        try:
            if idx_or_url[:4] == 'http':
                pattern = re.compile("idx=([0-9]+)")
                search = pattern.search(idx_or_url)
                result = search.group(1)
                return result
            else:
                return idx_or_url
        except TypeError:
            return None
        except AttributeError:
            return None


def test_some_using_mongodb():
    '''
    See
     - SQL to MongoDB mapping chart

     - primary key --> primary_key=True

    >>> test_some_using_mongodb()
    '''
    connect('aaabbb')

    # List all recruit
    recruits = list(Recruit.objects)
    for a in recruits:
        a.delete()

    companies = list(Company.objects)
    for a in companies:
        a.delete()

    assert len(Recruit.objects) == 0

    company = Company()
    company.name = "달수네"
    # I not unique, NotUniqueError
    company.idx = 'saramin93920'
    company.save()

    # It has id such as 50b21f13e138232f4abf0964
    #print company.id
    recruit = Recruit()
    recruit.memo = "머지 이건"
    recruit.rating = '5'
    recruit.company = company
    recruit.idx = 'saramin13705451'
    recruit.save()

    # Select
    assert Recruit.objects(idx='saramin13705451')[0].memo == u"머지 이건"

    assert list(Recruit.objects(idx='saramin13705452')) == []

    ### data modification
    # We couldn't change data from _data dictionary. _data just represent
    # data.
    ab = Recruit.objects(idx='saramin13705451')
    ak = ab[0]
    ak._data['rating'] = '2'
    ak.save()
    assert ak['rating'] == '2'
    assert ak.rating == '2'

    # rating is 2. But data to be stored is '5'.
    ac = Recruit.objects(idx='saramin13705451')
    assert ac[0].rating == '5'

    # We can change data from attribute
    del ab
    del ak
    del ac
    ab = Recruit.objects(idx='saramin13705451')
    ak = ab[0]
    ak.rating = '10'
    ak.save()

    ac = Recruit.objects(idx='saramin13705451')
    assert ac[0].rating == '10'

    recruit.delete()
    company.delete()



