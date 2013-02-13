#!/usr/bin/python
# coding: utf-8

import json
from datetime import datetime, timedelta
from mongoengine import connect

from db import Recruit, RecruitInfo
import config


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


