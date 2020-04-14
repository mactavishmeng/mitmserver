import httpsserver
import dnsserver
import http.server
import ssl
import _thread
import json


def starthttp(ip, port, proxy, isHTTPS=False, certfile=None, keyfile=None):

    # set proxy address and port of Burpsuite or Fiddler...
    httpsserver.proxies = proxy

    try:
        # create local server
        httpd = http.server.HTTPServer((ip, port), httpsserver.MyHandler)
        if isHTTPS:
            if certfile is not None and keyfile is not None:
                httpd.socket = ssl.wrap_socket(httpd.socket, certfile=certfile, keyfile=keyfile, server_side=True)
                print ("simple https server, address:%s:%d" % (ip, port))
            else:
                print(certfile,keyfile)
                print("Certfile and Keyfile missing. Running in HTTP mode.")
        else:
            print ("simple http server, address:%s:%d" % (ip, port))
        httpd.serve_forever()
    except FileNotFoundError as e:
        print("Certfile and Keyfile missing.")
        exit(0)


def startdns(dns_list, enable_query=False):
    sev = dnsserver.SinDNSServer()
    for item in dns_list:
        sev.addname(item["host"], item["address"])
    if enable_query:
        sev.enable_query()
    print("simple DNS server is running")
    sev.start()  # start DNS server

if __name__ == '__main__':
    config = json.load(open("./mitmserver.json", 'r'))
    proxies = config["proxies"]
    try:
        for item in config["http_list"]:
            if item['ishttps']:
                _thread.start_new_thread(starthttp, (item['address'], item['port'], proxies, item['ishttps'], item['certfile'], item['keyfile']))
            else:
                _thread.start_new_thread(starthttp, (item['address'], item['port'], proxies))
        _thread.start_new_thread(startdns, (config["dns_list"], True))
    except Exception as e:
        print(e)
        print("ERROR!")
        exit(0)

while 1:
    pass