# PySkyPlusHD

Python package to control a Sky+ HD box

### Install
```
pip install PySkyPlusHD
```

### Example
```python
import PySkyPlusHD

sky = PySkyPlusHD.SkyBox("192.168.0.2")

# Pauses the Sky box
sky.sendButton("pause")

 # Returns True if on, False if off
state = sky.getState()

storage = sky.getStorage()
# Returns storage used in GB
usedGB = storage.usedGB
# Returns percentage of storage used
usedPercent = storage.usedPercent
```

### Buttons

Buttons supported by `sendButton`
```
power
select
backup
dismiss
channelup
channeldown
interactive
sidebar
help
services
search
tvguide
home
i
text
up
down
left
right
red
green
yellow
blue
0
1
2
3
4
5
6
7
8
9
play
pause
stop
record
fastforward
rewind
boxoffice
sky
```