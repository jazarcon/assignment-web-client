#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0', 
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7", 
            "Accept-Language" : "en-US,en;q=0.9", 
            "Accept-Encoding" : "gzip, deflate, br", 
            "Upgrade-Insecure-Requests" : "1"}

        request_headers = f""
        for header_name, header_value in headers.items():
            request_headers += f"{header_name}: {header_value}\r\n"
        request_headers += "\r\n"  # End of headers

        for header_name, header_value in headers.items():
            request_headers += f"{header_name}: {header_value}\r\n"
        request_headers += "\r\n"

        return request_headers

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    
    def parsedURL(self, url):
        # used https://docs.python.org/3/library/urllib.parse.html to understand how to use urllib.parse.urlparse()
        parsed_url= urllib.parse.urlparse(url)              # 
        host= parsed_url.hostname                           # 
        path= parsed_url.path                               # 
        port = parsed_url.port if parsed_url.port else 80   # assuming port 80 is ok

        return host, port, path
    
    def GET(self, url, args=None):
        code = 500
        body = ""

        host, port, path= self.parsedURL(url)

        # GET request
        self.connect(host, port)                                        # open conenction
        self.sendall(f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n")    # send request
        response_data = self.recvall(self.socket)                       # data from GET request
        self.close()

        # append headers 
        response_data += self.get_headers(response_data)
        print("after adding headers")
        print(response_data)

        response_lines = response_data.split('\r\n')
        status_line = response_lines[0]

        # Extract the status code from the status line
        status_code = int(status_line.split(' ')[1])
        print("checking status")
        print(status_code)

        # # response
        if status_code==301:
            return HTTPResponse(code=status_code, body=response_data)
        if status_code==302:
            return HTTPResponse(code=status_code, body=response_data)
        if status_code== 200:
            return HTTPResponse(code=status_code, body=response_data)
        if status_code==404:
            return HTTPResponse(code=status_code, body="Not Found")

    def POST(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.parsedURL(url)

        # POST request
        body = urllib.parse.urlencode(args) if args else ""
        contentLength = len(body)

        self.connect(host, port)
        request = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Length: {contentLength}\r\n\r\n{body}"
        self.sendall(request)
        response_data = self.recvall(self.socket)
        self.close()
        
        # response
        if not response_data:
            return HTTPResponse(code=200, body="")

        if "HTTP/1.0 404" in response_data:
            return HTTPResponse(code=404, body="Not Found")
        else:
            return HTTPResponse(code=200, body=response_data.split('\r\n\r\n')[1])

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
