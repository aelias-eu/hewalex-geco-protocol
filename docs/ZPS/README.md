# Communication
Communication with the G-422 controller unit is performed via RS485 line. Default communication parameters are 38400 8N1. The connector is on the back of the controller.
I have tested this via USB/R485 converter and now I'm using a Moxa RS485/LAN serial server to connect to the controller via LAN. You should be fine with any RS485 connection method.

# Packets
I'm assuming that the base request is MEMORY_REGISTERS request. 
This is a sample packet requesting data from controller:
`69 02 01 84 00 00 0c f6 02 00 01 00 40 80 00 32 64 00 bd b2`

We can divide the packet into two parts:
- Packet header
- Payload

Each of these parts has it's own CRC

| Packet header | Description |
|---|---|
|0x69|Packet start|
|0x02|Target address *(maybe the physical RS485 address, haven't tested yet)*|
|0x01|Sender address *(maybe the physical RS485 address, haven't tested yet)*|
|0x84|UNKNOWN|
|0x00|UNKNOWN|
|0x00|UNKNOWN|
|0x0c|Payload size|
|0xf6|Header CRC ( CRC-8/DVB-S2 ) [Online CRC Calculator](https://crccalc.com/?crc=69%2002%2001%2084%2000%2000%200c&method=crc8&datatype=hex&outtype=hex)
|*Payload*||
|0x02| Target address|
|0x00||
|0x01| Sender address|
|0x00| |
|0x40| Probably function ID - looks like the answer has the same number but with the 5th bit set to "1" (request: 40, answer 50; request 60, answer 70) |
|0x80| |
|0x00| |
|0x32| For function ID 40 and 50 this is the number of MEMORY REGISTERS (Bytes) requested|
|0x64| For function ID 40 and 50 this is the starting byte (in this example we are requesting 50(0x32) memory registers MEMORY REGISTER, staring from 100(0x64)|
|0x00| |
|0xbdb2| CRC-16/XMODEM [Online CRC Calculator](https://crccalc.com/?crc=02%2000%2001%2000%2040%2080%2000%2032%2064%2000&method=crc16&datatype=hex&outtype=hex) |

You can find more in the attached **hewalex_protocol_analysis.ods** file

It looks like the payload data is represented by 16bit registers and negative numbers are represented by the 2’s Complement Method [https://www.tutorialspoint.com/negative-binary-numbers]. 

This approach works for almost all data - except for:
 - Date
 - Time
 - Solar power
 - Total Energy
 - Scheduling settings for circulation- they are in binary form
For now it's implemented this way in the python script.
