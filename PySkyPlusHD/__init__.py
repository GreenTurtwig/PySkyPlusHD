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
        self._ip = ip
        self.serial = None
        self._skyBrowseURL = None 
        self._initialise()

    def _initialise(self):
        try:
            req = requests.get(f"http://{self._ip}:{PHOTO_PORT}"
                               f"/photo-viewing/start?uri=",
                               timeout=5)
        except requests.exceptions.RequestException:
            raise RuntimeError("No Sky box found. Check that the box is on and "
                            "the IP is correct.") from None

        for i in range(50):
            addr = f"http://{self._ip}:{UPNP_PORT}/description{i}.xml"
            head = {"User-Agent": "SKY"}
            req = requests.get(addr, headers=head, timeout=2)
            if req.status_code == 200:
                res = ElementTree.fromstring(req.text)
                if res[1][0].text == "urn:schemas-nds-com:device:SkyServe:2":
                    self.serial = res[1][4].text
                    self._skyBrowseURL = res[1][11][1][3].text
                    break

    def sendButton(self, button):
        button = BUTTONS[button]
        data = bytearray([4, 1, 0, 0, 0, 0,math.floor(224 + (button / 16)),
                          button % 16])

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1000)
        sock.connect((self._ip, SOCKET_PORT))

        recv = sock.recv(1024)
        sock.sendall(recv[:13])
        recv = sock.recv(1024)
        sock.sendall(recv[:2])

        sock.sendall(data)
        data[1] = 0
        sock.sendall(data)

        sock.close()

    def getState(self):
        url = f"http://{self._ip}:{PHOTO_PORT}/photo-viewing/start?uri="
        req = requests.get(url)
        state = True if req.status_code == 200 else False
        return state

    def getStorage(self):
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
        head = {"SOAPACTION":
                   '"urn:schemas-nds-com:service:SkyBrowse:2#Browse"',
                   "Content-Type": "text/xml"}
        req = requests.post(f"http://{self._ip}:{UPNP_PORT}{self._skyBrowseURL}", data=data, headers=head)
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
                             "maxGB", "usedGB", "usedPercent", "freePercent"])
        return storage(maxKB, usedKB, maxMB, usedMB, maxGB, usedGB,
                       usedPercent, freePercent)
