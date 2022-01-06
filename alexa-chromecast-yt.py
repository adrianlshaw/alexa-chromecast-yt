#!/usr/bin/env python3
# cert generation: openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
# debugging: curl https://localhost -X POST -k 
# -H "Content-Type: application/json" --data '{"username":"xyz","password":"xyz"}'

import pychromecast
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
from bs4 import BeautifulSoup
import requests
import sys
import re
import http.server
import time
import datetime
import ssl
from http.server import BaseHTTPRequestHandler
import cgi
import json
import _thread
import threading

class S(BaseHTTPRequestHandler):

    test_response = """
{
  "version": "1.0",
  "sessionAttributes": {},
  "response": {
    "outputSpeech": {
      "type": "PlainText",
      "text": "I'm opening YouTube on the Chromecast"
    },
    "card": {
      "type": "Simple",
      "title": "Casted",
      "content": "Sent to TV"
    },
    "reprompt": {
      "outputSpeech": {
        "type": "PlainText",
        "text": "Can I help you with anything else?"
      }
    },
    "shouldEndSession": true
  }
}

"""

    ip = None

    def timestamp(self, string):
        print((datetime.datetime.fromtimestamp(time.time()).strftime('%S')) + " " + str(string))

    def cast(self, input):

       input.replace(" ","+") 
    
       url = "https://www.youtube.com/results?search_query=" + input

       self.timestamp("Getting url")
       response = requests.get(url)
       page = response.text
       soup = BeautifulSoup(page,"lxml")
       self.timestamp("got URL")
       videotag = soup.find('button', {"data-video-ids" : re.compile(r".*")})
       
       if (len(videotag) == 0):
           print("Fail")

       VIDEO_ID= videotag['data-video-ids']
       CAST_NAME = "Chromecast TV"

       self.timestamp("finding chromecast")
       if S.ip is None:
           self.timestamp("not cached")
           chromecasts = pychromecast.get_chromecasts()
           print("number of chromecasts " + str(len(chromecasts)))
           try:
               cast = next(cc for cc in chromecasts if cc.device.friendly_name == CAST_NAME)
               #cast.wait()
               S.ip = cast.host
           except StopIteration:
               print("The Chromecast is offline!")
               return
       else:
           self.timestamp("cached")
       requrl = "http://" + str(self.ip) + ":8008/apps/YouTube"
       data = "v="+str(VIDEO_ID)
       self.timestamp("found chromecast")
       status = requests.post(requrl, data=data)
       print (status.status_code)
       self.timestamp(" casted")


    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json;charset=UTF-8')
        self.end_headers()

    def do_GET(self):
        print("hello?")
        self._set_headers()
        self.wfile.write(self.test_response.encode('utf-8'))
        print("Replied")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        value = ""
        dont_reply = False
        content_type = self.headers.get('Content-Type')
        print(str(content_type))
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        try:
            request = json.loads(post_body.decode('utf-8'))
            if request is None:
                print("Empty json")
            else:
                print(json.dumps(request, indent=4, sort_keys=True))
                value = request['request']['intent']['slots']['Query']['value']
                if str(request['request']['type']) == "SessionEndedRequest":
                    dont_reply = True
                print ("VALUE IS " + str(value))
                # Launch new thread
                start = time.time()
                thread = threading.Thread(target=self.cast, args=(value,))
                thread.start()
                end = time.time()
                elapsed = end - start
                #_thread.start_new_thread(self.cast, ("ThreadID", value))
        except json.decoder.JSONDecodeError:
            print("Failed to decode JSON")
        except KeyError:
            print("Not a valid request")

        if dont_reply == False:
            print("Replying")
            #self.send_header('Content-type', 'application/json;charset=UTF-8')
            self.send_response(200)
            self.end_headers()
            self.wfile.write(self.test_response.replace("YouTube", value).encode('utf-8'))
        return


httpd = http.server.HTTPServer(('0.0.0.0', 3000), S) 
#httpd.socket = ssl.wrap_socket (httpd.socket, certfile='./server.pem', server_side=True)
httpd.serve_forever()
