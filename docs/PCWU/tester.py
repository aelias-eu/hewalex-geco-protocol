#!/usr/bin/python

from binascii import unhexlify
from binascii import hexlify
import serial
from datetime import datetime
import time

MasterHardId = 1
MasterSoftId = 1

#SlaveHardId = 5
#SlaveSoftId = 6
SlaveHardId = 2
SlaveSoftId = 2

#IsSendMode = True
IsSendMode = False

#StandardMessagesTruncation = True
StandardMessagesTruncation = False
#ShowMessageBytes = False
#OnlyNotificationAndError = True
ShowMessageBytes = True
OnlyNotificationAndError = False

temp = {
    'T1': 8,
    'T2': 10,
    'T3': 12,
    'T4': 14,#
    'T5': 16,#
    'T6': 18,
    'T7': 20,
    'T8': 22,
    'T9': 24,
    'T10': 26
  }

POLY = 0xD5
def crc8(buf):
    if len(buf) == 0:
        return 0
    
    accum = 0
    for i in buf:
        accum = accum ^ i
        for _ in range(8):
            if accum & 0x80:
                accum = (((accum << 1) & 0xff) ^ POLY) & 0xff
            else:
                accum = (accum << 1) & 0xff
    
    return accum

POLY16 = 0x1021
def crc16(buf):
    if len(buf) == 0:
        return 0
    
    accum = 0
    for i in buf:
        accum = accum ^ (i << 8)
        for _ in range(8):
            if accum & 0x8000:
                accum = (((accum << 1) & 0xffff) ^ POLY16) & 0xffff
            else:
                accum = (accum << 1) & 0xffff
    
    return accum

def parseHardHeader(m):
  if len(m) < 8:
    raise Exception("Too short message")
  calcCrc = crc8(m[:7])
  return {
      "StartByte": m[0],
      "To": m[1],
      "From": m[2],
      "ConstBytes": (m[5] << 16) | (m[4] << 8) | m[3],
      "Payload": m[6],
      "CRC8": m[7],
      "CalcCRC8": calcCrc
    }

def validateHardHeader(h):
  if h["StartByte"] != 0x69:
    raise Exception("Invalid Start Byte")
  if h["CRC8"] != h["CalcCRC8"]:
    raise Exception("Invalid Hard CRC8")
  if h["ConstBytes"] != 0x84:
    raise Exception("Invalid Const Bytes")
  if h["From"] != MasterHardId and h["From"] != SlaveHardId:
    raise Exception("Invalid From Hard Address: " + str(h["From"]))
  if h["To"] != MasterHardId and h["To"] != SlaveHardId:
    raise Exception("Invalid To Hard Address: " + str(h["To"]))
  if h["To"] == h["From"]:
    raise Exception("From and To Hard Address Equal")

def getWord(w):
  return (w[1] << 8) | w[0]

def getDWord(w):
  return (w[3] << 24) | (w[2] << 16) | (w[1] << 8) | w[0]

def getWordReverse(w):
  return (w[0] << 8) | w[1]

def parseSoftHeader(h, m):
  if len(m) != h["Payload"]:
    raise Exception("Invalid soft message len")
  if len(m) < 12:
    raise Exception("Too short soft message")
  calcCrc = crc16(m[:h["Payload"]-2])
  return {
      "To": getWord(m[0:]),
      "From": getWord(m[2:]),
      "FNC": m[4],
      "ConstByte": getWord(m[5:]),
      "RegLen": m[7],
      "RegStart": getWord(m[8:]),
      "RestMessage": m[10:h["Payload"]-2],
      "CRC16": getWordReverse(m[h["Payload"]-2:]),
      "CalcCRC16": calcCrc
    }

def validateSoftHeader(h, sh):
  if sh["CRC16"] != sh["CalcCRC16"]:
    raise Exception("Invalid Soft CRC16")
  if sh["ConstByte"] != 0x80:
    raise Exception("Invalid Const Soft Byte 0x80")
  if (h["From"] == MasterHardId and sh["From"] != MasterSoftId) or (h["From"] == SlaveHardId and sh["From"] != SlaveSoftId):
    raise Exception("Invalid From Slave Address")
  if (h["To"] == MasterHardId and sh["To"] != MasterSoftId) or (h["To"] == SlaveHardId and sh["To"] != SlaveSoftId):
    raise Exception("Invalid To Slave Address")

def getTemp(w):
  w = getWord(w)
  if w & 0x8000:
    w = w - 0x10000
  return w / 10.0

def getSchedule(w1):
  w = getDWord(w1)
  toRet = {}
  for i in range(0,24):
    toRet[i] = 1 if w & (1 << i) else 0
  return toRet

def convertoToScheduleProtoData(s):
  toRet = [0, 0, 0, 0]
  for by in range(0,3):
    for bi in range(0, 8):
      if s[by * 8 + bi]:
        toRet[by] = toRet[by] | (1 << bi)
  return toRet

def parseX60Message(m):
  ret = {}
  ret["date"] = "20{:02d}-{:02d}-{:02d}".format(m[0], m[1], m[2]) #m[3] Day Of Week 0 = Monday
  ret["time"] = "{:02d}:{:02d}:{:02d}".format(m[4], m[5], m[6]) #m[7] always 0, probably for proper aligment
  ret["unknown5"] = hex(getWord(m[46:]))
  ret["unknown3"] = hex(getWord(m[72:])) #org 73
  ret["IsManual"] = getWord(m[74:])
  ret["unknown1"] = hex(getWord(m[76:]))
  ret["EV1"] = getWord(m[78:]) #unknown4
  ret["unknown2"] = hex(m[82])
  ret["unknown6"] = hex(getWord(m[86:]))
  ret["unknown7"] = hex(getWord(m[90:]))
  ret["unknown8"] = hex(getWord(m[98:]))
  ret["unknown9"] = hex(getWord(m[100:]))
  for name in temp:
    ret[name] = getTemp(m[temp[name]:])
  return ret

def printStandardX60Message(m):
  mp = parseX60Message(m)
  if (m[28:46] == b'\x14\x05\x14\x05\x14\x05\x14\x05\x0c\xfe\x0c\xfe\x01\x00\x01\x00\x01\x00' and
    m[48:72] == b'\x03\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x02\x00\x02\x00\x02\x00\x02\x00\x03\x00\x03\x00' and
    m[80:82] == b'\x00\x00' and
    m[83:86] == b'\x00\x00\x00' and
    m[88:90] == b'\x00\x00' and
    m[92:98] == b'\xeb\x83\x1aC\x1f\x00' and
    m[102:] == b'\xcd\x9d'):
    print("StandardNotification=" + str(mp))
  else:
    mp["RestMessage"] = hexlify(m)
    print("NoStandardNotification=" + str(mp))

def printMessage(h, sh):
  print ({
    'hard': {
      "StartByte": hex(h["StartByte"]),
      "To": h["To"],
      "From": h["From"],
      "ConstBytes": hex(h["ConstBytes"]),
      "Payload": h["Payload"],
      "CRC8": hex(h["CRC8"])
    },
    'soft': {
      "To": sh["To"],
      "From": sh["From"],
      "FNC": hex(sh["FNC"]),
      "ConstByte": hex(sh["ConstByte"]),
      "RegLen": sh["RegLen"],
      "RegStart": str(sh["RegStart"]) + " (" + hex(sh["RegStart"]) + ")",
      "RestMessage": hexlify(sh["RestMessage"]),
      "CRC16": hex(sh["CRC16"])
    }
  })

def printStandardMessage(h, sh):
  if h["From"] == MasterHardId and sh["FNC"] == 0x40 and sh["RegStart"] == 100 and sh["RegLen"] == 20 and len(sh["RestMessage"]) == 0:
    if not OnlyNotificationAndError:
      print("Standard request to read 20 registers at address 100")
  elif h["To"] == MasterHardId and sh["FNC"] == 0x50 and sh["RegStart"] == 100 and sh["RegLen"] == 20 and sh["RestMessage"] == b'\x18\x90\x01o\x01\x00\x80\x02\x1c\x00\x1c\x90\x01o\x01\x00h\t\x1c\x00':
    if not OnlyNotificationAndError:
      print("Standard response to read 20 registers at address 100")
  elif h["From"] == (SlaveHardId if IsSendMode else MasterHardId) and (sh["FNC"] == 0x50 if IsSendMode else sh["FNC"] == 0x60) and sh["RegStart"] == 120 and sh["RegLen"] == 104 and len(sh["RestMessage"]) == 104:
    printStandardX60Message(sh["RestMessage"])
  elif h["To"] == MasterHardId and sh["FNC"] == 0x70 and sh["RegStart"] == 120 and sh["RegLen"] == 104 and len(sh["RestMessage"]) == 0:
    if not OnlyNotificationAndError:
      print("Standard notification response to read 104 registers at address 120")
  elif h["From"] == MasterHardId and sh["FNC"] == 0x40 and sh["RegStart"] == 252 and sh["RegLen"] == 4 and len(sh["RestMessage"]) == 0:
    if not OnlyNotificationAndError:
      print("Standard request to read 4 registers at address 252")
  elif h["To"] == MasterHardId and sh["FNC"] == 0x50 and sh["RegStart"] == 252 and sh["RegLen"] == 4 and sh["RestMessage"] == b'\x10\x00\x00\x00':
    if not OnlyNotificationAndError:
      print("Standard response to read 4 registers at address 252")
  elif h["From"] == (SlaveHardId if IsSendMode else MasterHardId) and (sh["FNC"] == 0x50 if IsSendMode else sh["FNC"] == 0x60) and sh["RegStart"] == 120 and sh["RegLen"] == 104 and len(sh["RestMessage"]) == 104:
    print("NoStandardNotificationMessage=", end='')
    printMessage(h, sh)
    print("NoStandardNotification=" + str(parseX60Message(sh["RestMessage"])))
  else:
    print("NoStandardMessage=", end='')
    printMessage(h, sh)

def processMessage(m, ignoreTooShort):
  h = parseHardHeader(m)
  validateHardHeader(h)
  ml = h["Payload"]
  if ignoreTooShort and ml + 8 > len(m):
    #print("Ignore short message " + str(ml) + " " + str(len(m)))
    return m
  sh = parseSoftHeader(h, m[8:ml+8])
  if not StandardMessagesTruncation and not OnlyNotificationAndError:
    printMessage(h, sh)
  validateSoftHeader(h, sh)
  if StandardMessagesTruncation:
    printStandardMessage(h, sh)
  elif h["From"] == MasterHardId and (sh["FNC"] == 0x50 if IsSendMode else sh["FNC"] == 0x60) and sh["RegStart"] == 120 and sh["RegLen"] == 104 and len(sh["RestMessage"]) == 104:
    print(parseX60Message(sh["RestMessage"]))
  return m[ml+8:]

def getReadMessageBytes(m):
  h = parseHardHeader(m)
  validateHardHeader(h)
  ml = h["Payload"]
  sh = parseSoftHeader(h, m[8:ml+8])
  validateSoftHeader(h, sh)
  return sh["RestMessage"]

def processAllMessages(m, returnRemainingBytes=False):
  if ShowMessageBytes:
    print(hexlify(m))
  minLen = 8 if returnRemainingBytes else 0
  prevLen = len(m)
  while prevLen > minLen:
    m = processMessage(m, returnRemainingBytes)
    if len(m) == prevLen:
      if returnRemainingBytes:
        return m
      raise Exception("Something wrong")
    prevLen = len(m)
  return m

def timingTest(ser):
  results = []
  lastTime = time.monotonic_ns()
  chtime = lastTime
  endTime = lastTime + 1000 * 1000 * 1000 * 3 #3 sec
  chlen = 0
  lr = {
    "dt": datetime.now(),
    "tm": [0]
  }
  results.append(lr)
  ser.flushInput()
  while lastTime < endTime:
    c = ser.read(1)
    if len(c) == 0:
      continue
    chlen = chlen + 1
    curTime = time.monotonic_ns()
    diff = int((curTime - lastTime) / (1000 * 1000))
    lastTime = curTime
    if diff > 10:
      diffch = int((curTime - chtime) / (1000 * 1000)) - diff
      chtime = curTime
      lr["tm"].append({
          "diff": diffch,
          "chlen": chlen
        })
      if diff > 100:
        lr = {
          "dt": datetime.now(),
          "tm": [{
          "diff": diff,
          "chlen": 0
        }]
        }
        results.append(lr)
      else:
        lr["tm"].append({
          "diff": diff,
          "chlen": 0
        })
      chlen = 0
  for r in results:
    if r["tm"][0] != 0:
      print("+{}ms".format(r["tm"][0]["diff"]))
    
    print("{} {}".format(r["dt"].strftime("%H:%M:%S.%f"), " ".join(["+" + str(x["diff"]) + "ms (" + ((str(x["chlen"]) + "c") if x["chlen"] != 0 else "space") + ")" for x in r["tm"][1:]])))

def createReadMessage():
  header = [0x69, SlaveHardId, MasterHardId, 0x84, 0, 0]
  payload = [(SlaveSoftId & 0xff), ((SlaveSoftId >> 8) & 0xff), (MasterSoftId & 0xff), ((MasterSoftId >> 8) & 0xff), 0x40, 0x80, 0, 104, 120, 0]
  calcCrc16 = crc16(payload)
  payload.append((calcCrc16 >> 8) & 0xff)
  payload.append(calcCrc16 & 0xff)
  header.append(len(payload))
  calcCrc8 = crc8(header)
  header.append(calcCrc8)
  return bytearray(header + payload)

def createReadMessage1():
  header = [0x69, SlaveHardId, MasterHardId, 0x84, 0, 0]
  payload = [(SlaveSoftId & 0xff), ((SlaveSoftId >> 8) & 0xff), (MasterSoftId & 0xff), ((MasterSoftId >> 8) & 0xff), 0x40, 0x80, 0, 20, 100, 0]
  calcCrc16 = crc16(payload)
  payload.append((calcCrc16 >> 8) & 0xff)
  payload.append(calcCrc16 & 0xff)
  header.append(len(payload))
  calcCrc8 = crc8(header)
  header.append(calcCrc8)
  return bytearray(header + payload)

def createReadMessage2():
  header = [0x69, SlaveHardId, MasterHardId, 0x84, 0, 0]
  payload = [(SlaveSoftId & 0xff), ((SlaveSoftId >> 8) & 0xff), (MasterSoftId & 0xff), ((MasterSoftId >> 8) & 0xff), 0x40, 0x80, 0, 76, 224, 0]
  calcCrc16 = crc16(payload)
  payload.append((calcCrc16 >> 8) & 0xff)
  payload.append(calcCrc16 & 0xff)
  header.append(len(payload))
  calcCrc8 = crc8(header)
  header.append(calcCrc8)
  return bytearray(header + payload)

def createReadMessage3():
  header = [0x69, SlaveHardId, MasterHardId, 0x84, 0, 0]
  payload = [(SlaveSoftId & 0xff), ((SlaveSoftId >> 8) & 0xff), (MasterSoftId & 0xff), ((MasterSoftId >> 8) & 0xff), 0x40, 0x80, 0, 100, 0x2C, 1] # 300 = 0x12C, 400 = 0x190, 500 = 0x1F4
  calcCrc16 = crc16(payload)
  payload.append((calcCrc16 >> 8) & 0xff)
  payload.append(calcCrc16 & 0xff)
  header.append(len(payload))
  calcCrc8 = crc8(header)
  header.append(calcCrc8)
  return bytearray(header + payload)

def createReadMessage4():
  header = [0x69, SlaveHardId, MasterHardId, 0x84, 0, 0]
  payload = [(SlaveSoftId & 0xff), ((SlaveSoftId >> 8) & 0xff), (MasterSoftId & 0xff), ((MasterSoftId >> 8) & 0xff), 0x40, 0x80, 0, 100, 0x90, 1] # 300 = 0x12C, 400 = 0x190, 500 = 0x1F4
  calcCrc16 = crc16(payload)
  payload.append((calcCrc16 >> 8) & 0xff)
  payload.append(calcCrc16 & 0xff)
  header.append(len(payload))
  calcCrc8 = crc8(header)
  header.append(calcCrc8)
  return bytearray(header + payload)

def createReadMessage5():
  header = [0x69, SlaveHardId, MasterHardId, 0x84, 0, 0]
  payload = [(SlaveSoftId & 0xff), ((SlaveSoftId >> 8) & 0xff), (MasterSoftId & 0xff), ((MasterSoftId >> 8) & 0xff), 0x40, 0x80, 0, 38, 0xf4, 1] # 300 = 0x12C, 400 = 0x190, 500 = 0x1F4
  calcCrc16 = crc16(payload)
  payload.append((calcCrc16 >> 8) & 0xff)
  payload.append(calcCrc16 & 0xff)
  header.append(len(payload))
  calcCrc8 = crc8(header)
  header.append(calcCrc8)
  return bytearray(header + payload)

def createReadMessageReg(reg):
  header = [0x69, SlaveHardId, MasterHardId, 0x84, 0, 0]
  payload = [(SlaveSoftId & 0xff), ((SlaveSoftId >> 8) & 0xff), (MasterSoftId & 0xff), ((MasterSoftId >> 8) & 0xff), 0x40, 0x80, 0, 2, reg & 0xff, (reg >> 8) & 0xff]
  calcCrc16 = crc16(payload)
  payload.append((calcCrc16 >> 8) & 0xff)
  payload.append(calcCrc16 & 0xff)
  header.append(len(payload))
  calcCrc8 = crc8(header)
  header.append(calcCrc8)
  return bytearray(header + payload)

def createReadMessageReg32(reg):
  header = [0x69, SlaveHardId, MasterHardId, 0x84, 0, 0]
  payload = [(SlaveSoftId & 0xff), ((SlaveSoftId >> 8) & 0xff), (MasterSoftId & 0xff), ((MasterSoftId >> 8) & 0xff), 0x40, 0x80, 0, 4, reg & 0xff, (reg >> 8) & 0xff]
  calcCrc16 = crc16(payload)
  payload.append((calcCrc16 >> 8) & 0xff)
  payload.append(calcCrc16 & 0xff)
  header.append(len(payload))
  calcCrc8 = crc8(header)
  header.append(calcCrc8)
  return bytearray(header + payload)

def createWriteMessage16(reg, val):
  header = [0x69, SlaveHardId, MasterHardId, 0x84, 0, 0]
  payload = [(SlaveSoftId & 0xff), ((SlaveSoftId >> 8) & 0xff), (MasterSoftId & 0xff), ((MasterSoftId >> 8) & 0xff), 0x60, 0x80, 0, 2, reg & 0xff, (reg >> 8) & 0xff, val & 0xff, (val >> 8) & 0xff]
  calcCrc16 = crc16(payload)
  payload.append((calcCrc16 >> 8) & 0xff)
  payload.append(calcCrc16 & 0xff)
  header.append(len(payload))
  calcCrc8 = crc8(header)
  header.append(calcCrc8)
  return bytearray(header + payload)

def createWriteMessageArray(reg, val):
  header = [0x69, SlaveHardId, MasterHardId, 0x84, 0, 0]
  payload = [(SlaveSoftId & 0xff), ((SlaveSoftId >> 8) & 0xff), (MasterSoftId & 0xff), ((MasterSoftId >> 8) & 0xff), 0x60, 0x80, 0, len(val), reg & 0xff, (reg >> 8) & 0xff] + val
  calcCrc16 = crc16(payload)
  payload.append((calcCrc16 >> 8) & 0xff)
  payload.append(calcCrc16 & 0xff)
  header.append(len(payload))
  calcCrc8 = crc8(header)
  header.append(calcCrc8)
  return bytearray(header + payload)

def createReadMessageRegTime():
  header = [0x69, SlaveHardId, MasterHardId, 0x84, 0, 0]
  reg = 120
  payload = [(SlaveSoftId & 0xff), ((SlaveSoftId >> 8) & 0xff), (MasterSoftId & 0xff), ((MasterSoftId >> 8) & 0xff), 0x40, 0x80, 0, 8, reg & 0xff, (reg >> 8) & 0xff]
  calcCrc16 = crc16(payload)
  payload.append((calcCrc16 >> 8) & 0xff)
  payload.append(calcCrc16 & 0xff)
  header.append(len(payload))
  calcCrc8 = crc8(header)
  header.append(calcCrc8)
  return bytearray(header + payload)

def createWriteMessageTime():
  header = [0x69, SlaveHardId, MasterHardId, 0x84, 0, 0]
  dt = datetime.now()
  reg = 120
  payload = [(SlaveSoftId & 0xff), ((SlaveSoftId >> 8) & 0xff), (MasterSoftId & 0xff), ((MasterSoftId >> 8) & 0xff), 0x60, 0x80, 0, 8, reg & 0xff, (reg >> 8) & 0xff, (dt.year - 2000) & 0xff, dt.month & 0xff, dt.day  & 0xff, t.weekday() & 0xff, dt.hour & 0xff, dt.minute & 0xff, dt.second & 0xff, 0]
  calcCrc16 = crc16(payload)
  payload.append((calcCrc16 >> 8) & 0xff)
  payload.append(calcCrc16 & 0xff)
  header.append(len(payload))
  calcCrc8 = crc8(header)
  header.append(calcCrc8)
  return bytearray(header + payload)

#m = unhexlify('6902018400000cf602000100408000326400bdb2')
ser = serial.Serial('/dev/ttySC1', 38400, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
#timingTest(ser)
ser.flushInput()
m = ser.read(500)
m = ser.read(500)
r = processAllMessages(m)

ser.close()

exit(0)

#loop

StandardMessagesTruncation = True
ShowMessageBytes = False
OnlyNotificationAndError = True
ser = serial.Serial('/dev/ttySC1', 38400, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.1)
ser.flushInput()
m = ser.read(500)
prevM = b''
while True:
  readed = ser.read(500)
  if len(readed) == 0:
    readed = ser.read(500)
  if len(readed) == 0:
    readed = ser.read(500) #try 3 times, interval is 350ms, timeout is 100ms, so should be enought
  m = prevM + readed
  prevM = processAllMessages(m, returnRemainingBytes=True)

ser.close()

exit(0)

#send

IsSendMode = True
ser = serial.Serial('/dev/ttySC1', 38400, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.5)
ser.flushInput()

ser.write(createReadMessage3())
m = ser.read(500)
r = processAllMessages(m)


exit(0)

ser.flushInput()

ser.write(createReadMessageReg32(432))
m = ser.read(500)
getSchedule(getReadMessageBytes(m))

ser.write(createWriteMessageArray(440, convertoToScheduleProtoData({0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 0, 16: 1, 17: 1, 18: 1, 19: 1, 20: 0, 21: 1, 22: 1, 23: 1})))
m = ser.read(500)
r = processAllMessages(m)

exit(0)


ser.flushInput()

ser.write(createReadMessageReg(430))
m = ser.read(500)
r = processAllMessages(m)

ser.write(createWriteMessage16(430, 1))
m = ser.read(500)
r = processAllMessages(m)

exit(0)

ser.flushInput()
ser.write(createReadMessageRegTime())
m = ser.read(500)
r = processAllMessages(m)
ser.write(createWriteMessageTime())
m = ser.read(500)
r = processAllMessages(m)
