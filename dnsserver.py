import socketserver
import struct
import socket
import time

# DNS Query
class SinDNSQuery:
    def __init__(self, data):
        i = 1
        self.name = ''
        while True:
            d = data[i]
            if d == 0:
                break;
            if d < 32:
                self.name = self.name + '.'
            else:
                self.name = self.name + chr(d)
            i = i + 1
        self.querybytes = data[0:i + 1]
        (self.type, self.classify) = struct.unpack('>HH', data[i + 1:i + 5])
        self.len = i + 5
    def getbytes(self):
        return self.querybytes + struct.pack('>HH', self.type, self.classify)

# DNS Answer RRS
# this class is also can be use as Authority RRS or Additional RRS
class SinDNSAnswer:
    def __init__(self, ip):
        self.name = 49164
        self.type = 1
        self.classify = 1
        self.timetolive = 190
        self.datalength = 4
        self.ip = ip
    def getbytes(self):
        res = struct.pack('>HHHLH', self.name, self.type, self.classify, self.timetolive, self.datalength)
        s = self.ip.split('.')
        res = res + struct.pack('BBBB', int(s[0]), int(s[1]), int(s[2]), int(s[3]))
        return res

# DNS frame
# must initialized by a DNS query frame
class SinDNSFrame:
    def __init__(self, data):
        (self.id, self.flags, self.quests, self.answers, self.author, self.addition) = struct.unpack('>HHHHHH', data[0:12])
        self.query = SinDNSQuery(data[12:])
    def getname(self):
        return self.query.name
    def setip(self, ip):
        self.answer = SinDNSAnswer(ip)
        self.answers = 1
        self.flags = 33152
    def getbytes(self):
        res = struct.pack('>HHHHHH', self.id, self.flags, self.quests, self.answers, self.author, self.addition)
        res = res + self.query.getbytes()
        if self.answers != 0:
            res = res + self.answer.getbytes()
        print("[%s][DNS] Query: %s, Answer: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.query.name, self.answer.ip))
        return res

# A UDPHandler to handle DNS query
class SinDNSUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        dns = SinDNSFrame(data)
        skt = self.request[1]
        if dns.query.type==1:
            # If this is query a A record, then response it
            ip = self.findname(dns.getname())

            # When error occurred or default query disabled.
            if ip == "0.0.0.0":
                skt.sendto(data, self.client_address)
            else:
                dns.setip(ip)
                skt.sendto(dns.getbytes(), self.client_address)
        else:
            # If this is not query a A record, ignore it
            skt.sendto(data, self.client_address)

    def findname(self, name):
        if SinDNSServer.namemap.__contains__(name):
            return SinDNSServer.namemap[name]
        else:
            name_list = name.split(".")
            for pos in range(1, len(name_list)):
                test_name = "*." + ".".join(name_list[pos:])
                if SinDNSServer.namemap.__contains__(test_name):
                    return SinDNSServer.namemap[test_name]

        if SinDNSServer.enable_query:
            try:
                res = socket.getaddrinfo(name, None)
                return res[0][-1][0]
            except socket.gaierror:
                return "0.0.0.0"
        else:
            return "0.0.0.0"

# DNS Server
# It only support A record query
# user it, U can create a simple DNS server
class SinDNSServer:
    namemap = {}
    enable_query = False
    def __init__(self, port=53):
        self.port = port

    def addname(self, name, ip):
        self.namemap[name] = ip

    def enable_query(self):
        self.enable_query = True

    def start(self):
        HOST, PORT = "0.0.0.0", self.port
        server = socketserver.UDPServer((HOST, PORT), SinDNSUDPHandler)
        server.serve_forever()

# Now, test it
if __name__ == "__main__":
    sev = SinDNSServer()
    sev.addname('www.aa.com', '192.168.0.1')    # add a A record
    sev.addname('www.bb.com', '192.168.0.2')    # add a A record
    sev.addname('*', '0.0.0.0') # default address
    sev.start() # start DNS server

# Now, U can use "nslookup" command to test it
# Such as "nslookup www.aa.com"