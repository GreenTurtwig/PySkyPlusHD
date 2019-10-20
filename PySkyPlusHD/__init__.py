import math
import requests
import socket

from xml.etree import ElementTree
from collections import namedtuple

from .buttons import BUTTONS
SOCKET_PORT = 49160
PHOTO_PORT = 49159
UPNP_PORT = 49153

class SkyBox:
    def __init__(self, ip):
        self.ip = ip
    
    def sendButton(self, button):
        button = BUTTONS[button]
        data = bytearray([4, 1, 0, 0, 0, 0,math.floor(224 + (button / 16)),
                          button % 16])

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1000)
        sock.connect((self.ip, SOCKET_PORT))

        recv = sock.recv(1024)
        sock.sendall(recv[:13])
        recv = sock.recv(1024)
        sock.sendall(recv[:2])

        sock.sendall(data)
        data[1] = 0
        sock.sendall(data)

        sock.close()
    
    def getState(self):
        url = f"http://{self.ip}:{PHOTO_PORT}/photo-viewing/start?uri="
        req = requests.get(url)
        state = True if req.status_code == 200 else False
        return state
    
    def getStorage(self):
        url = f"http://{self.ip}:{UPNP_PORT}/description3.xml"
        headers = {"User-Agent": "SKY"}
        req = requests.get(url, headers=headers)
        res = ElementTree.fromstring(req.text)
        descURL = f"http://{self.ip}:{UPNP_PORT}{res[1][11][1][3].text}"

        data = """<s:Envelope
                      xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
                      <s:Body>
                          <u:Browse
                              xmlns:u="urn:schemas-nds-com:service:SkyBrowse:2"
                              >
                              <SortCriteria/>
                              <RequestedCount>1</RequestedCount>
                              <StartingIndex>0</StartingIndex>
                              <Filter>*</Filter>
                              <BrowseFlag>BrowseMetadata</BrowseFlag>
                              <ObjectID>3</ObjectID>
                          </u:Browse>
                      </s:Body>
                  </s:Envelope>"""
        headers = {"SOAPACTION":
                   '"urn:schemas-nds-com:service:SkyBrowse:2#Browse"',
                   "Content-Type": "text/xml"}
        req = requests.post(f"{descURL}", data=data, headers=headers)
        res = ElementTree.fromstring(req.text)[0][0][0].text
        res = ElementTree.fromstring(res)[0][2].attrib

        maxKB = int(res["maxSize"])
        usedKB = int(res["usedSize"])
        maxMB =  round(maxKB / 1000)
        usedMB = round(usedKB / 1000)
        maxGB = round(maxMB / 1000, 1)
        usedGB = round(usedMB / 1000, 1)
        usedPercent = round((usedKB / maxKB) * 100, 2)
        freePercent = round(((maxKB - usedKB) / maxKB) * 100, 2)

        storage = namedtuple("storage", ["maxKB", "usedKB", "maxMB", "usedMB",
                             "maxGB", "usedGB", "percentUsed", "percentFree"])
        return storage(maxKB, usedKB, maxMB, usedMB, maxGB, usedGB,
                       percentUsed, percentFree)