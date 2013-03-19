#!/usr/bin/python
# coding: utf-8

"""
This script installs or uninstalls samdolc on your system.
-------------------------------------------------------------------------------
Usage: install.py [OPTIONS] COMMAND

Commands:
    install                  Install to /usr/local

    uninstall                Uninstall from /usr/local

    zip			     Create tarball

Options:
    --dir <directory>     Install or uninstall in <directory>
                             instead of /usr/local

    --prefix <directory>  Install or uninstall in <directory>
                             instead of /usr/local
"""


import os
import sys
import getopt
import shutil


cur_file_path = os.path.abspath(__file__)
cur_dir_path = os.path.dirname(cur_file_path)
server_path = cur_dir_path + '/server'
if server_path not in sys.path:
    sys.path.insert(0, server_path)
import config


class Libs(object):
    '''
    >>> Libs.file_list('file_list') #doctest: +SKIP
    '''
    @staticmethod
    def file_list(path):
        result = []
        fd = open(path, 'r')
        content = fd.read()
        fd.close()
        for a in content.split('\n'):
            if not a == '':
                result.append(a)
        return result


class Var:
    '''

    >>> Var.prefix
    '/usr/local'
    >>> Var.prefix = '/usr/share/local'
    >>> Var.prefix
    '/usr/share/local'
    >>> Var.install_dir()
    '/usr/share/local/share/samdolc'
    >>> Var.dir = 'samdolc'
    >>> Var.install_dir()
    '/usr/share/local/samdolc'

    >>> Var.prefix = '/usr/share/local/'
    >>> Var.install_dir()
    '/usr/share/local/samdolc'
    
    >>> Var.current_dir #doctest: +SKIP

    # Variables are static. Restore the variables
    >>> Var.prefix = '/usr/local'
    >>> Var.dir = 'share/samdolc'
    '''

    files = Libs.file_list('file_list_on_rpm')

    files_extension = ('samdolc.crx')

    required_packages = (('lxml', 0),
                         ('PyQt4', 0),
                         ('python-daemon', 0)
                         )

    prefix = '/usr/local'

    current_dir = os.path.dirname(os.path.realpath(__file__))



    dir = 'share/samdolc'

    @staticmethod
    def install_dir():
        def addSlush(str):
            if str[-1:] == "/": return str
            else: 		return str + "/"

        if Var.dir:
            return addSlush(Var.prefix) + Var.dir
        else:
            return Var.prefix


# From http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")
        

def usage():
    print __doc__
    sys.exit(1)

def subprocess(cmdline):
    '''
    used so that we can capture the return value of an executed command.

    >>> #subprocess('ls')
    '''
    import subprocess
    proc = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
    data, err = proc.communicate()
    return proc.wait(), data, err


def zip():
    '''
    >>> #subprocess('make zip')

    '''
    ret = subprocess('make zip')
    print ret[1]


def install():
    if not Var.dir:
        print 'There is no directory name. It can \
invoke a critical problem such as "$rm /usr/local"'
        exit(1)

    for path in Var.files:

        src_filename = Var.current_dir + '/' + path
        dst_filename = Var.install_dir() + '/' + path
        dst_directory = os.path.dirname(dst_filename)

        if not os.path.isdir(dst_directory):
            os.makedirs(dst_directory)

        shutil.copy(src_filename, dst_directory)
        print 'Installed', dst_filename


service_script_base = '''#!/bin/sh

# chkconfig: 2345 55 25
# description: Tool to help my recruit.

PID_FILE=%s

case $1 in
    start)
	. %s
	python %s start
	;;
    stop) # code to stop the service
	kill `cat $PID_FILE`
esac
'''

def _service_script():
    '''
    >>> _service_script() #doctest: +SKIP
    '''
    dst_directory = Var.install_dir()
    virtualenv_activate_filename = dst_directory + '/bin/activate'
    daemon_executable = dst_directory + '/server/samdolcd_linux.py'
    daemon_pid_path = config.daemon_pid_file_path
    return service_script_base % (daemon_pid_path,
                                  virtualenv_activate_filename,
                                  daemon_executable)

def install_service():
    '''
    >>> #install_service()
    '''
    initd_path = '/etc/init.d/'
    initd_script_name = initd_path + 'samdolc'
    if os.path.exists(initd_script_name):
        print "There is already the service script"
        exit(1)
    try:
        with open(initd_script_name, 'w') as f:
            f.write(_service_script())
            f.close()
            print '   ==> ', initd_script_name, 'is installed'
            os.chmod(initd_script_name, 0755)
            print '   ==> ', initd_script_name, 'is to be 0755'

    except IOError as e:
        print "You seems doesn't have correct permisstion for %s." % initd_path
        print repr(e)
        exit(1)


chrome_external_json_base = '''{ \
    "external_crx": "%s",
    "external_version": "%s"
}'''


def install_chrome_extension():
    '''
    >>> install_chrome_extension()
    '''
    target_directory = '/opt/google/chrome/extensions'
    chrome_external_filename = 'onpobpkjhjihnhmjpjemcedjebllieoi.json'
    chrome_external_full_path = target_directory + '/' + chrome_external_filename
    chrome_extension_version = config.chrome_extension_version
    chrome_extension_path = Var.install_dir() + '/samdolc.crx'

    chrome_external_json = chrome_external_json_base % \
        (chrome_extension_path, str(chrome_extension_version))

    if os.path.exists(chrome_external_full_path):
        print "There is already the service script"
        exit(1)

    try:
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        with open(chrome_external_full_path, 'w') as f:
            f.write(chrome_external_json)
            f.close()
            print '   ==> ', chrome_external_full_path, 'is installed'
    except IOError as e:
        print "You seems doesn't have correct permisstion for %s." % target_directory
        print repr(e)
        exit(1)
        

def uninstall():
    if not Var.dir:
        print 'There is no directory name. It can \
invoke a critical problem such as "$rm /usr/local"'
        exit(1)

    path = Var.install_dir()
    if os.path.exists(path):
        shutil.rmtree(path)
    else:
        print "There is no", path
        exit(1)


def check_dependencies():
    print 'Checking dependencies ...\n'
    print 'Required dependencies:'

    for package in Var.required_packages:
        name, version = package
        try:
            # TODO: version error
            module = __import__(name)
            # assert module.VERSION >= version
            print '   ==> ', name, '.................... OK'
        except ImportError:
            print '   ==> ', name, '.................... Not found'

        except AssertionError:
            print '   ==> ', name, '.................... version Error'




def main():
    try:
        print sys.argv[1:]
        opts, args = getopt.gnu_getopt(sys.argv[1:], '', ['dir=', 'prefix='])
    except getopt.GetoptError:
        usage()

    for opt, value in opts:
        if opt == '--dir' or opt == '--prefix':
            Var.prefix = value
            if not os.path.isdir(Var.prefix):
                print '\nError:', Var.prefix, ' does not exist.'
                usage()

    if args == ['install']:
        check_dependencies()
        print 'Installing samdol to', Var.prefix, '...\n'
        if not os.access(Var.prefix, os.W_OK):
            print 'You do not have write permissions to', Var.prefix
            sys.exit(1)

        install()

    elif args == ['install_service']:
        print 'Installing service', '...\n'
        install_service()

    elif args == ['install_chrome_extension']:
        print 'Installing chrome_extension', '...\n'
        install_chrome_extension()


    elif args == ['uninstall']:
        print 'Uninstalling samdol from', Var.install_dir(), '...\n'
        uninstall()

    elif args == ['zip']:
        print 'Zipping samdol\n'
        zip()
    else:
        usage()

if __name__ == "__main__":
    main()
