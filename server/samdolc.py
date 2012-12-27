#!/usr/bin/python
# coding: utf-8

import BaseHTTPServer
import urllib
import re
import logging
import json

import config
from db import RecruitInfo
from parser import SaraminContainer
import view

from libs import parseURL


# TODO: Let's use dictionary
class SamdolcRequest(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        host, path, params, query = parseURL(self.path)
        command = path[1:]

        if command == 'get':
            # Search db and response infos
            url = query['url']
            info = RecruitInfo(url)
            # New recruit will has {} repr(info)
            self.wfile.write(repr(info))

            logging.info("Url(get command): %s" % repr(parseURL(self.path)))
            logging.debug("Recruit: %s\n" % repr(info))

            #logging.info("Url(Quoted): %s" % urllib.unquote(self.path))

        elif command == 'post':
            # Fixme: It requires few second to parse. Use thread.
            info = RecruitInfo()
            if info.isNew(query['url']):
                sc = SaraminContainer(query['url'])
                sc.get()
                query.update(sc.infos)

            info.getFromJson(query)
            info.save()

            self.wfile.write("ok")
            logging.info("Query(post command): %s\n" % query)
            #logging.info("Url(Quoted): %s" % urllib.unquote(self.path))

        elif command == 'calendar':
            import calendar
            self.send_response(200, 'text/html')
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            print view.calendar()
            self.wfile.write(view.calendar())

        elif command == 'recruits':
            # result = {}
            # result['title'] = 'This is title'
            # result['start'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            # result['url'] = 'http://google.com'
            self.wfile.write(view.recruits())

        else:
            if self.path[1:6] == 'tools':
                content = ''
                try:
                    fd = open(self.path[1:], 'r')
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
                    
                self.send_response(200, text_type)
                self.send_header('Content-Type', text_type)
                self.end_headers()
                self.wfile.write(content)


    def _idxFromQuery(self, query):
        content = query['url']
        pattern = re.compile("idx=([0-9]+)")
        search = pattern.search(content)
        result = search.group(1)
        return result


def main():
    ""
    logging.basicConfig(level=config.debug_level)
    server_address = (config.server_address, config.server_port)
    httpd = BaseHTTPServer.HTTPServer(server_address, SamdolcRequest)

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    try:
        httpd.serve_forever()
    except: print "end server"

if __name__ == '__main__':
    main()
