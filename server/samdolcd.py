#!/usr/bin/python
# coding: utf-8

'''
On linux
$ samdolcd.py start|stop|restart

On Windows
$ python.exe service2.py  --startup="auto" install
$ python.exe service2.py  --startup="auto" remove
'''


import os

if os.name == 'nt':
    from samdolcd_windows import main
else:
    from samdolcd_linux import main

if __name__ == "__main__":
    main()
