#!/usr/bin/python
# coding: utf-8

import BaseHTTPServer
import SocketServer
import urllib
import re
from collections import Counter

import config
from db import RecruitInfo
from container_bloker import ContainerBloker

import view
from libs import *

class SamdolcResponse(Counter):
    def code(self): pass
    def msg(self):  pass

    
class SamdolcAction(object):
    def __init__(self, request_obj):
        self.obj = request_obj
        self.host, self.path, self.params, self.query = parseURL(self.obj.path)
        self.query_string = self.path[1:]
        self.wfile = self.obj.wfile

        self.response = dict()
        self.__setResponse()
        
        self.commands = self.__getCommands()   #all commands

    # TODO: I need more flexible response method
    def __setResponse(self):
        "Basic errors. The form is determined in self.__wfileError."
        self.response['UnknownException'] = ['400', '<font color=red><b>UnknownError</b></font>']
        self.response['NoContainerException'] = ['401', '<font color=red><b>Not supported url!</b></font>']
        self.response['AttributeError'] = ['402', '<font color=blue><b>It is new!</b></font>']
        self.response['ConnectionError'] = ['403', '<font color=red><b>The database server has on problem!</b></font>']

        self.response['OK'] = ['100', 'OK']
        
    def __getCommands(self):
        result = getDecoratedMethods(self.__class__)
        for method in result:
            if not any('command' in deco for deco in result[method]):
                del result[method]
        return result

    def _wfileMedia(self):
        content = ''

        try:
            # The server doesn't knows the current directory if you use
            # py2exe. So use abpath.
            base_path = config.current_abpath
            abpath_filename = base_path + self.path[1:]
            fd = open(abpath_filename, 'r')
            content = fd.read()
            config.logger.debug("The length of media file is %s" % str(len(content)))
            fd.close()
        except IOError, err:
            config.logger.error(err)
            return

        if self.path[-3:] == ".js":
            text_type = "text/javascript"
        elif self.path[-3:] == "css":
            text_type = "text/css"
        else:
            text_type = None
            
        self.obj.send_response(200, text_type)
        self.obj.send_header('Content-Type', text_type)
        self.obj.end_headers()
        self.wfile.write(content)

        
    def dododo(self):
        config.logger.debug(self.query_string)
        config.logger.debug("Path is %s", self.obj.path)
        if self.query_string in self.commands.keys():
            config.logger.debug(self.query_string)
            method = getattr(self, self.query_string)
            method()
        elif self.path[1:6] == 'tools' or self.path[1:7] == 'medias':
            config.logger.debug("This is media file")
            self._wfileMedia()
                

    def command(f):
        "The decorator for the command. Use this decorator to register a command."
        return f

    def __wfileError(self, exception_name):
        try:
            status_code = self.response[exception_name][0]            
            msg = self.response[exception_name][1]
        except KeyError:
            status_code = self.response['UnknownException'][0]
            msg = self.response['UnknownException'][1]

        response = '{"status": "%s", "msg": "%s"}' % (status_code, msg)
        self.wfile.write(response)
        config.logger.debug(response)

    @command
    def get(self):
        #print self.obj.request
        # Search db and response infos
        url = self.query['url']
        try:
            info = RecruitInfo(url)
        except Exception, err:
            #config.logger.info(repr(err))
            exception_name = err.__class__.__name__
            self.__wfileError(exception_name)
            config.logger.debug(exception_name)
            return

        # New recruit will has {} as the result repr(info). It is NoneType
        info_repr = repr(info)

        # TODO: more elegant
        if not info_repr == '{}':
            self.wfile.write(repr(info))
        else:
            self.__wfileError('AttributeError')
            
        config.logger.info("Url(get command): %s" % repr(parseURL(self.path)))
        config.logger.debug("Recruit: %s\n" % repr(info))
        #config.logger.info("Url(Quoted): %s" % urllib.unquote(self.path))
        
    @command
    def post(self):
        info = RecruitInfo()
        if info.isNew(self.query['url']):
            sc = ContainerBloker(self.query['url'])
            self.query.update(sc.get().infos)

        info.getFromJson(self.query)
        info.save()

        self.wfile.write(self.__wfileError('OK'))
        config.logger.info("Query(post command): %s\n" % self.query)
        #config.logger.info("Url(Quoted): %s" % urllib.unquote(self.path))

    @command
    def calendar(self):
        config.logger.info("On calendar method.")
        self.obj.send_response(200, 'text/html')
        self.obj.send_header('Content-Type', 'text/html')
        self.obj.end_headers()
        config.logger.debug("On calendar method. After send_header")
        #print view.calendar()
        config.logger.debug("=====================")
        config.logger.debug(repr(parseURL(self.path)))
        config.logger.debug("=====================")
        #config.logger.info(repr(view.calendar()))
        self.wfile.write(view.calendar())

    @command
    def allcalendar(self):
        config.logger.info("On calendar method.")
        self.obj.send_response(200, 'text/html')
        self.obj.send_header('Content-Type', 'text/html')
        self.obj.end_headers()
        config.logger.debug("On calendar method. After send_header")
        #print view.calendar()
        config.logger.debug("=====================")
        config.logger.debug(repr(parseURL(self.path)))
        config.logger.debug("=====================")
        #config.logger.info(repr(view.calendar()))
        self.wfile.write(view.allcalendar())
        

    def _recruits(self):
        # result = {}
        # result['title'] = 'This is title'
        # result['start'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        # result['url'] = 'http://google.com'
        self.wfile.write(view.recruits())

    @command
    def recruits(self):
        self.obj.send_response(200, 'text/html')
        self.obj.send_header('Content-Type', 'text/html')
        self.obj.end_headers()

        recruits = view.ViewRecruits()
        self.wfile.write(recruits)

    @command
    def permanents(self):
        self.obj.send_response(200, 'text/html')
        self.obj.send_header('Content-Type', 'text/html')
        self.obj.end_headers()

        recruits = view.ViewPermanentRecruits()
        self.wfile.write(recruits)

        

class SamdolcRequest(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):

        action = SamdolcAction(self)
        action.dododo()
        

    def _idxFromQuery(self, query):
        content = query['url']
        pattern = re.compile("idx=([0-9]+)")
        search = pattern.search(content)
        result = search.group(1)
        return result

class SamdolcHTTPServer (SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass
    # def serve_forever(self):
    #     self.stop_serving = False
    #     while not self.stop_serving:
    #         self.handle_request()

    # def stop(self):
    #     self.stop_serving = True



def main():
    ""
    server_address = (config.server_address, config.server_port)
    httpd = SamdolcHTTPServer(server_address, SamdolcRequest)

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    try:
        httpd.serve_forever()
    except: print "end server"



if __name__ == '__main__':
    main()
