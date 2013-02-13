#!/usr/bin/python
# coding: utf-8

import BaseHTTPServer
import SocketServer
import urllib
import re

from mongoengine.connection import ConnectionError

import config
from db import RecruitInfo
from container_bloker import ContainerBloker
import view
from libs import parseURL

class SamdolcAction(object):
    def __init__(self, request_obj):
        self.obj = request_obj
        self.host, self.path, self.params, self.query = parseURL(self.obj.path)
        self.command = self.path[1:]
        self.wfile = self.obj.wfile

    def dododo(self):
        try:
            config.logger.info(self.command)            
            method = getattr(self, self.command)
            method()
        except AttributeError:
            if self.path[1:6] == 'tools':
                content = ''

                try:
                    # The server doesn't knows the current directory if you use py2exe.
                    base_path = config.current_abpath
                    abpath_filename = base_path + self.path[1:]
                    fd = open(abpath_filename, 'r')
                    content = fd.read()
                    print type(content)
                    fd.close()
                except IOError:
                    print 'ioerror'
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

    def get(self):
        # Search db and response infos
        url = self.query['url']
        try:
            info = RecruitInfo(url)
        except ConnectionError, err:
            # Database doesn't work
            config.logger.error(repr(err))
            msg = '{"dberror": "True"}'
            self.wfile.write(msg)
            return

        # New recruit will has {} repr(info)
        self.wfile.write(repr(info))
        
        config.logger.info("Url(get command): %s" % repr(parseURL(self.path)))
        config.logger.debug("Recruit: %s\n" % repr(info))
        
        #config.logger.info("Url(Quoted): %s" % urllib.unquote(self.path))

    def post(self):
        info = RecruitInfo()
        if info.isNew(self.query['url']):
            sc = ContainerBloker(self.query['url'])
            self.query.update(sc.get().infos)

        info.getFromJson(self.query)
        info.save()

        self.wfile.write("ok")
        config.logger.info("Query(post command): %s\n" % self.query)
        #config.logger.info("Url(Quoted): %s" % urllib.unquote(self.path))

    def calendar(self):
        config.logger.info("On calendar method.")
        self.obj.send_response(200, 'text/html')
        self.obj.send_header('Content-Type', 'text/html')
        self.obj.end_headers()
        config.logger.info("On calendar method. After send_header")
        #print view.calendar()
        config.logger.info("=====================")
        config.logger.info(repr(parseURL(self.path)))
        config.logger.info("=====================")
        #config.logger.info(repr(view.calendar()))
        self.wfile.write(view.calendar())

    def recruits(self):
        # result = {}
        # result['title'] = 'This is title'
        # result['start'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        # result['url'] = 'http://google.com'
        self.wfile.write(view.recruits())


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
