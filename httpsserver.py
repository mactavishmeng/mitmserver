import http.server
import requests
import ssl
from urllib3.exceptions import InsecureRequestWarning
import urllib3.util.ssl_
import time

urllib3.disable_warnings(InsecureRequestWarning)
urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'

proxies={}

class MyHandler(http.server.BaseHTTPRequestHandler):
    def req(self):
        try:
            if isinstance(self.request, ssl.SSLSocket):
                scheme = "https://"
            else:
                scheme = "http://"
            # make URL from request
            self.url = scheme + self.headers["host"].strip("\n") + self.path

            # Get body length if has
            if self.headers.__contains__('Content-Length'):
                body_len = int(self.headers['Content-Length'])
            else:
                body_len = 0
            # Make request
            req = requests.Request(method=self.command, url=self.url, headers=self.headers, data=self.rfile.read(body_len))
            s = requests.Session()
            prepped = req.prepare()

            # send request via proxy
            r = s.send(prepped, verify=False, proxies=proxies, allow_redirects=False)
            
            # set response headers
            self.send_response(r.status_code)
            for key in r.headers:
                self.send_header(key, r.headers[key])
            self.end_headers()

            # set response body
            self.wfile.write(r.content)
        except IOError as e:
            print(e)
            self.send_error(404, 'file not found: %s' % self.path)
        except Exception as e:
            print(e)


    def do_GET(self):
        self.req()

    def do_POST(self):
        self.req()

    def do_HEAD(self):
        self.req()

    def do_OPTIONS(self):
        self.req()

    def do_PUT(self):
        self.req()

    def do_DELETE(self):
        self.req()

    def do_MOVE(self):
        self.req()

    def do_TRACE(self):
        self.req()

    def log_request(self, code='-', size='-'):
        print("[%s][HTTP] Request: (%s) %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), code, self.url))
        return True
