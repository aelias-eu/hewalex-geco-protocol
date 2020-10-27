# hewalex-geco-protocol
Communication tool for GECO G-422 range of solar pump controllers, used also (but not only) in the Hewalex ZPS-18e 

The **hewalex2mqtt.py** script will connect to the hewalex controller, request registers 100-250 and publish data to the MQTT broker.
You have to edit settings directly in the script.
Requests are hardcoded (asuming the controllers physical and also logical address is 1) so if you need to change them, you have to recalculate the CRC. 
I take it as working PoC.
