.. contents:: :local:


Purpose
=======

I am finding full time job. The bookmarking tool in work.go.kr has a
problem. The information is disappered when the end of recruit period. I
need a database what company has how many times recruit and some memos
with the recruit page.


Requirements
============

 - python
 - MongoEngine (require MongoDB)
 - lxml
 - PyQt4
 - python-daemon
 - cssselect
 - fullcalendar-1.5.4 (included)
 - jquery-1.3.2 (included)
 - jquery.json-2.4 (included)
 - jquery star rating (included)
 - jquery.qtip (included)
 - BeautifulSoup (optional)

 - PyWin32(On Windows. http://starship.python.net/~skippy/win32)
 - nsis(Nullsoft Scriptable Install System) for window installer
 - rpm-build for linux installer
 - chrome browser


lxml
----

On Windows, to install lxml you need to compile manually. See
 - http://lxml.de/build.html#static-linking-on-windows
You can also use pre-compiled package(unofficial) from
 - http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml


Using
=====

On Linux(Fedora)
--------

$ make rpm
will generate samdolc-{VERSION}.noarch.rpm.

$ sudo rpm -Uvh samdolc-{VERSION}.noarch.rpm

You also need to install google-chrome. See

 - http://www.if-not-true-then-false.com/2010/install-google-chrome-with-yum-on-fedora-red-hat-rhel/


On Windows(Tested on Windows 7 64bit, not work on xp)
----------

Easy way is to use prepacked rpm or "samdolc.exe". The installer
"samdolc.exe" is pre-packed by py2exe.

I am using the combination of mingw, cygwin, You can generate the installer with
$ mingw32-make exe-py2exe # Packed by py2exe. This means you don't need pre-installed python
or
$ mingw32-make exe        # You need pre-installed python and the required packages

Enable chrome-extension on chrome.


Use directly from source
------------------------

 0. Install the required packages
 
::

 $ su
 $ cat <<EOF > /etc/yum.repos.d/10gen.repo
 [10gen]
 name=10gen Repository
 #baseurl=http://downloads-distro.mongodb.org/repo/redhat/os/i686  #32bit
 baseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64 #64bit
 gpgcheck=0
 enabled=1
 EOF
 $ yum install PyQt4 python-lxml mongo-10gen mong-10gen-server
 $ pip install virtualenv
 $ exit
 
 $ virtualenv samdolc
 $ cd samdolc
 $ source bin/activate
 $ pip install -r requirements.txt

It has two part
 - server
 - chrome_extension

 1. Configure the server such as port, database name
 ::

  $ nano samdol/server/config.py

 2. Start server
 ::

  $ cd samdol/server
  $ python samdolc.py

 2.1. To start as a daemon::

 $ python samdolcd.py start

 3. Install chrome extension

 3.1. Type "chrome://extensions" in url bar

 3.2. Check "Developer mode"

 3.3. Click "Load unpacked extension..."

 3.4. Load samdol/chrome_extension

 4. You can see a browser action button in chrome

 5. Find the recruit such as http://www.saramin.co.kr/zf_user/recruit/recruit-view?idx=13845172

 6. Click browser action button

 7. Click "Submit"


To see calendar, connect
"http://localhost:8559/calendar"(http://127.0.0.1/calendar on Windows)





TODO
====

See
 - todo.muse
 - issues.muse
