#!/usr/bin/python3
import serial

# change these data according to your needs
ser = serial.Serial('/dev/ttyUSB0', 38400)
mqttBroker ="127.0.0.1" 				# IP addres or DNS name of your MQTT broker
mqttPrefix="hewalex/"					# MQTT Topic prefix 

def twos_complement(hexstr,bits):
  # Source: https://stackoverflow.com/questions/6727875/hex-string-to-signed-int-in-python-3-2 
  # Author: Mark Tolonen ( https://stackoverflow.com/users/235698/mark-tolonen )
  value = int(hexstr,16)
  if value & (1 << (bits-1)):
   value -= 1 << bits
  return value

ser.flushInput()
import paho.mqtt.client as mqtt 
client = mqtt.Client("HEWALEX")
client.connect(mqttBroker) 

from binascii import unhexlify
from binascii import hexlify

def HewalexRequest(requestID):
  if requestID == 1:
    print("Requesting bytes 100-149")
    ser.write(unhexlify('6902018400000cf602000100408000326400bdb2'))		# request 0x32 (50) registers from 0x64 (100)
  if requestID == 2:
    print("Requesting bytes 150-199")
    ser.write(unhexlify('6902018400000cf602000100408000329600c811'))		# request 0x32 (50) registers from 0x96 (150)
  if requestID == 3:
    print("Requesting bytes 200-249")
    ser.write(unhexlify('6902018400000cf60200010040800032c800e5a1'))		# request 0x32 (50) registers from 0xc8 (200)

def HewalexWaitForResponse(timeout):
  print("Waiting for response.")
  ser.timeout=int(timeout)
  response=ser.read(70)
  print("Response:")
  respSize = len(response)
  print(respSize)
  print(hexlify(bytearray(response)))
  print(response[0])
  if respSize == 70 and response[0]==0x69:
    print("Packet Header")
    print("-From:    ",response[1])
    print("-To:      ",response[2])
    print("-[3,4,5]: ",hexlify(response[3:6]))		 # ToDo: verify - response[3] always 0x84
    print("-Payload: ",response[6]," Bytes")
    print("-CRC:     ",response[7]," CRC-8/DVB-S2 ")		 # ToDo: check CRC validity
    ## verify packet size based on packet length && payload length from header
    print("Data header")
    print("-From:    ",response[8])				 # Logical address? 
    print("-To:      ",response[10])				 # Logical address?
    print("-FNC:     ",response[12])
    print("-[13]:    ",response[13])
    print("-Length:  ",response[15]," Bytes")
    print("-Start#   ",response[16]," Byte[",response[16]," to ",int(response[16])+int(response[15]),"]")
    fncID = int(response[12])
    if fncID == 0x50:
      startReg = int(response[16])
      for iPacketPos in range(0,int(response[15])):
       if (iPacketPos % 2 == 0):
        iReg = iPacketPos+startReg
        processed = 0
        hexstr=hexlify(bytearray([response[19+iPacketPos],response[18+iPacketPos]]))
        if iReg==120:						#date
          client.publish(mqttPrefix+"decoded/"+"controllerDate", "20"+str(response[18+iPacketPos])+"-"+str(response[18+iPacketPos+1])+"-"+str(response[18+iPacketPos+2]))
          processed = 1
        if iReg==124:						#time
          client.publish(mqttPrefix+"decoded/"+"controllerTime", str(response[18+iPacketPos]).zfill(2)+":"+str(response[18+iPacketPos+1]).zfill(2)+":"+str(response[18+iPacketPos+2]).zfill(2))
          processed = 1
        if iReg==128:						#T1
          client.publish(mqttPrefix+"decoded/T1",twos_complement(hexstr,16))
          processed = 1
        if iReg==130:						#T2
          client.publish(mqttPrefix+"decoded/T2",twos_complement(hexstr,16))
          processed = 1
        if iReg==132:						#T3
          client.publish(mqttPrefix+"decoded/T3",twos_complement(hexstr,16))
          processed = 1
        if iReg==134:						#T4
          client.publish(mqttPrefix+"decoded/T4",twos_complement(hexstr,16))
          processed = 1
        if iReg==136:						#T5
          client.publish(mqttPrefix+"decoded/T5",twos_complement(hexstr,16))
          processed = 1
        if iReg==138:						#T6
          client.publish(mqttPrefix+"decoded/T6",twos_complement(hexstr,16))
          processed = 1
        if iReg==144:
          client.publish(mqttPrefix+"decoded/SolarPower",int(hexstr,16))
          processed = 1
        if iReg==148:
          client.publish(mqttPrefix+"decoded/Reg148",twos_complement(hexstr,16))
          processed = 1
        if iReg==150:
          client.publish(mqttPrefix+"decoded/CollectorPumpON",int(hexstr,16))
          processed = 1
        if iReg==152:
          client.publish(mqttPrefix+"decoded/Flow",twos_complement(hexstr,16)/10)
          processed = 1
        if iReg==154:
          client.publish(mqttPrefix+"decoded/Reg154",twos_complement(hexstr,16))
          processed = 1
        if iReg==156:
          client.publish(mqttPrefix+"decoded/Reg156",twos_complement(hexstr,16))
          processed = 1
        if iReg==166:
          client.publish(mqttPrefix+"decoded/TotalEnergy",int(hexstr,16)/10)
        # only unprocessed data goes to /raw topic
        if processed == 0:
          client.publish(mqttPrefix+"raw/"+str(iReg),hexstr)
          #client.publish(mqttPrefix+"raw/"+str(iReg)+'/val',twos_complement(hexstr,16))
         

HewalexRequest(1)
HewalexWaitForResponse(1)
HewalexRequest(2)
HewalexWaitForResponse(1)
HewalexRequest(3)
HewalexWaitForResponse(1)



def menuPrint():
  print(" Make a choice:")
  print(" [1] Request registers 100-149")
  print(" [2] Request registers 150-199")
  print(" [3] Request registers 200-249")
  print(" [4] Exit")
  print("==============================")

#menuPrint()
#choice=input("Enter number {1..4}: ")
#if choice.isnumeric():
#  if int(choice) > 0 and int(choice) < 4:
#    HewalexRequest(int(choice))
#    HewalexWaitForResponse(5)
