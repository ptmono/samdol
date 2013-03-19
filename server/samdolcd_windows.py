#from http://stackoverflow.com/questions/5315193/how-to-keep-a-windows-service-running
#python.exe service2.py  --startup="auto" install
#python.exe service2.py  --startup="auto" remove
from win32api import CloseHandle, GetLastError, SetConsoleCtrlHandler
import os
import sys
import time

import win32serviceutil
import win32service
import win32event
import servicemanager

import traceback

import config
from samdolc import SamdolcHTTPServer, SamdolcRequest

server_address = (config.server_address, config.server_port)
httpd = SamdolcHTTPServer(server_address, SamdolcRequest)


class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "samdolc"
    _svc_display_name_ = "samdolc"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        SetConsoleCtrlHandler(lambda x: True, True)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)


    def SvcStop(self):
        # import os
        # os.popen('taskkill /F /IM pythonservice.exe')

        #httpd.stop()
        #httpd.shutdown()
        httpd.socket.close()

        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False

        # status = win32serviceutil.StopService( svc_name, machine)[1]
        # while status == STOPPING:
        #     time.sleep(1)
        #     status = svcStatus( svc_name, machine)
        # return status


    def SvcDoRun(self):

        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.run = True
        # try: # try main
        #     self.main()
        # except:
        #     servicemanager.LogErrorMsg(traceback.format_exc()) # if error print it to event log
        #     os._exit(-1)#return some value other than 0 to os so that service knows to restart
        
        httpd.serve_forever()

    def main(self):
        samdolc.main()


def main():
    win32serviceutil.HandleCommandLine(AppServerSvc)

if __name__ == '__main__':
    main()
