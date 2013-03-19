#!/usr/bin/python
# coding: utf-8

import json
from datetime import datetime, timedelta
from mongoengine import connect
from jinja2 import Environment, FileSystemLoader, Markup

from db import Recruit, RecruitInfo
import config

class Var:
    http_header = "Content-type: text/html; charset=utf-8\n\n"
    page_not_found_msg = "We has no page %s"



base_html = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<link rel='stylesheet' type='text/css' href='./tools/fullcalendar-1.5.4/fullcalendar/fullcalendar.css' />
<link rel='stylesheet' type='text/css' href='./tools/fullcalendar-1.5.4/fullcalendar/fullcalendar.print.css' media='print' />
<script type='text/javascript' src='./tools/fullcalendar-1.5.4/jquery/jquery-1.8.1.min.js'></script>
<script type='text/javascript' src='./tools/fullcalendar-1.5.4/jquery/jquery-ui-1.8.23.custom.min.js'></script>
<script type='text/javascript' src='./tools/fullcalendar-1.5.4/fullcalendar/fullcalendar.min.js'></script>
<script type="text/javascript" src="./tools/jquery.qtip-1.0.0-rc3.min.js"></script>
<script type='text/javascript'>

$(document).ready(function() {
    
    var date = new Date();
    var d = date.getDate();
    var m = date.getMonth();
    var y = date.getFullYear();
    
    $('#calendar').fullCalendar({
	editable: true,
	events: %s,

	eventRender: function(event, element) {
	    element.qtip({
		content: event.recruit_summary + '<p><font color="blue">' + event.memo +
		'</font>'
		
	    });
	}
    });
});


</script>
<style type='text/css'>

body {
    margin-top: 40px;
    text-align: center;
    font-size: 14px;
    font-family: "Lucida Grande",Helvetica,Arial,Verdana,sans-serif;
}

#calendar {
    width: 900px;
    margin: 0 auto;
}

th { font-size: 12px; }
td { font-size: 12px; }


</style>
</head>
<body>
<div id='calendar'></div>
</body>
</html>
'''


def calendar():
    config.logger.info("Start view.calendar()")
    dump = recruits()
    config.logger.debug(dump)
    return base_html % dump


def recruits():
    config.logger.info("Start view.recruits()")    
    try:
        connect(config.db_name)
        today = datetime.today()
        yesterday = today + timedelta(-1)
        recs = Recruit.objects
        config.logger.debug(recs)
        recs = Recruit.objects(end__gt = yesterday)
        config.logger.debug(recs)
    except Exception, err:
        config.logger.error(repr(err))
    return documents2jsondump(recs)

# def recruits():
#     pr = ViewRecruits()
#     return pr.getContent()


def _documents2jsondump(objs):
    result = []
    rec_temp = None
    for rec in objs:
        rec_temp = rec._data
        if rec_temp['end']:
            rec_temp['end'] = rec_temp['end'].strftime(config.time_format)
            result.append(rec_temp)

    return json.dumps(result)


def documents2jsondump(objs):
    result = []
    rec_temp = None
    for rec in objs:
        rec_temp = RecruitInfo()
        rec_temp.getFromObject(rec)
        result.append(rec_temp._repr())
    return json.dumps(result)


class ViewAbstract(object):
    def __init__(self):
        connect(config.db_name)
        self.jinja_env = Environment(loader=FileSystemLoader(config.medias_d))

        self.content = self.getContent()

    def getContent(self):
        pass

    def __repr__(self):
        return self.content


class ViewRecruits(ViewAbstract):
    def getContent(self):
        result = ''
        infos = self._getContent()
        infos = dict(articles=infos)
        # Render
        temp = self.jinja_env.get_template('jinja_list.html')
        result = temp.render(infos)

       # The result is unicode
        result = result.encode(config.char_set)
        return result

    def _getContent(self):
        # Get the rendered context 'temp_context
        info_l = []
        #infos = Recruit.objects(end = None)
        infos = Recruit.objects

        for info in infos:
            try:
                print info.to_mongo()
                end = info.end.strftime("%m-%d/%y")
                start = info.end.strftime("%m-%d/%y")                
            except:
                end = None
                start = None
            element = (info.title, start, end, info.rating,
                       info.memo, info.idx, info.url)
            info_l.append(element)
        info_l.reverse()
        return info_l

class ViewPermanentRecruits(ViewRecruits):
    def _getContent(self):
        # Get the rendered context 'temp_context
        info_l = []
        #infos = Recruit.objects(end = None)
        infos = Recruit.objects(end=None)

        for info in infos:
            try:
                print info.to_mongo()
                end = info.end.strftime("%m-%d/%y")
                start = info.end.strftime("%m-%d/%y")                
            except:
                end = None
                start = None
            element = (info.title, start, end, info.rating,
                       info.memo, info.idx, info.url)
            info_l.append(element)
        info_l.reverse()
        return info_l
        
        
