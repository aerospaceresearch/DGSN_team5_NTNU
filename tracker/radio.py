import socket

TCPPORT = 7356 # radio tcp port
HOST = '127.0.0.1' # radio host address
BUFFERSIZE = 256
 
class radio:

    ST_OK = "RPRT 0"
    ST_ERROR = "RPRT 1"
    MODE_OFF = "OFF"
    MODE_RAW = "RAW"
    MODE_AM = "AM"
    MODE_FM = "FM"
    MODE_WFM = "WFM"
    MODE_WFM_ST = "WFM_ST"
    MODE_LSB = "LSB"
    MODE_USB = "USB"
    MODE_CW = "CW"
    MODE_CWL = "CWL"
    MODE_CWU = "CWU"

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def cmd(self, cmd):
        self.tcp.send(cmd + "\n")
        return self.tcp.recv(BUFFERSIZE)

    # get current tuned frequency
    def getfreq(self):
        return self.cmd('f')

    # get current mode
    def getmode(self, mode):
        return self.cmd('m')

    # get signal strength
    def getlevel(self):
        return self.cmd('l')

    # tune to a frequency
    def tune(self, frequency):
        if self.cmd('F %d' % (frequency)) == self.ST_OK:
            return self.getfreq() - frequency
        else:
            return False

    # change receiver mode
    def mode(self, mode):
        if self.cmd('M ' + mode) == self.ST_OK:
            return self.getmode() == mode
        else:
            return False
    
    # close tcp connection
    def close(self):
        self.cmd('c')
        self.tcp.close()

    def aos(self):
        return self.cmd('AOS') == self.ST_OK

    def los(self):
        return self.cmd("LOS") == self.ST_OK

    def init(self):
        try:
            self.tcp.connect((HOST, TCPPORT))
        except socket.error:
            print " - Could not connect to radio at %s:%d. Is the TCP server turned on?\n" % (HOST, TCPPORT)
            exit()
        try :
            int(self.getfreq())
        except ValueError:
            print " - Received arbitrary radio frequency. Check port assignment"
            exit()
