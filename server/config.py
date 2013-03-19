#!/usr/bin/python
# coding: utf-8

from os.path import dirname, abspath

current_abpath = abspath(dirname(__file__)) + "/"
# With py2exe the dirname to be INSTPATH/server/library.zip. So
# current_abpath will be INSTPATH/server/library.zip/
if current_abpath[-12:] == "library.zip/":
    current_abpath = current_abpath[:-12]

version = "0.1"

chrome_extension_version = "0.1"


server_address = "localhost"
# If you change the port, you have to modify the port in chrome_extension
# manually.
server_port = 8559

db_name = 'aaabbb'
db_name_test = 'abtest'

time_format = '%Y-%m-%dT%H:%M:%S'

char_set = 'utf-8'

# The directory for js, html, css
medias_d = current_abpath + 'medias/'

# This file contains the pid of samdolc daemon
daemon_pid_file_path = '/tmp/samdolc.pid'

### === Logger
### ______________________________________________________________
import logging

LOG_TO_FILEP = True
if LOG_TO_FILEP:
    LOG_FILE_FILENAME = current_abpath + 'logging.log'
    LOG_FILE_MODE = 'a'
else:
    LOG_FILE_FILENAME = None
    LOG_FILE_MODE = None

LOG_FORMAT = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s'
LOG_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
LOG_LEVEL = logging.DEBUG

logging.basicConfig(filename=LOG_FILE_FILENAME,
                            filemode=LOG_FILE_MODE,
                            format=LOG_FORMAT,
                            datefmt=LOG_TIME_FORMAT,
                            level=LOG_LEVEL)
logger = logging.getLogger('samdolc')
