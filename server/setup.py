from distutils.core import setup
import py2exe
class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.version = '0.1'
        self.name = 'samdolc'

target = Target(
    description = 'samdolc',
    modules=['samdolcd_windows'],
    cmdline_style='pywin32'
)

setup(service = [target],
      console = ['samdolc.py'],
      options={
        'py2exe':
            {
            'includes': ['lxml.etree', 'lxml._elementpath', 'gzip', 'cssselect', 'sip', 'PyQt4.QtNetwork'],
            }
        }
      )
