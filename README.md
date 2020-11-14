# hewalex-geco-protocol
![G422](docs/g422-p07.jpeg)

Communication tool for GECO G-422 range of solar pump controllers, used also (but not only) in the Hewalex [ZPS 18e-01 ECO](https://www.hewalex.eu/en/offer/pump-groups-and-expansion-vessels/zps-18e-01-eco-pump-and-control-unit.html) Pump control unit

The **hewalex2mqtt.py** script will connect to the hewalex controller, request registers 100-250 and publish data to the MQTT broker.
## Configuration
You have to edit settings directly in the script.

On the top of the script file, you can change these 3 lines:

```
# change these data according to your needs
ser = serial.Serial('/dev/ttyUSB0', 38400)
mqttBroker ="127.0.0.1" 				# IP addres or DNS name of your MQTT broker
mqttPrefix="hewalex/"					# MQTT Topic prefix 
```
If you are connecting via some serial2ethernet converter (or rs485/ethernet converter like I am), you can use settings like this:
```
ser = serial.serial_for_url('socket://IP_ADDRESS_OF_CONVERTER:TCP_PORT')
```
For example:
```
ser = serial.serial_for_url('socket://192.168.0.12:6200')
```

Requests are hardcoded (asuming the controller's physical and also logical address is 2) so if you need to change them, you have to recalculate the CRC. 
I take it as working PoC. Currently I'm running it in cron from my armbian-based device and processing actual temperatures via MQTT to homeassistant.

![mqtt](docs/mqtt.png)

It is possible to send configuration data to the controller, but I don't have the communication device for Ekontrol connection - this would require some sniffing on such installation. 

If you look at the demo of [Ekontrol](https://ekontrol.pl/en/33570/scheme/) by Hewalex , you can see pretty much what can be done with this system. They don't seem to have any public API for the Ekontrol interface, so there is that...

This work is inspired & based on informations provided on the elektroda.pl forum 
- https://www.elektroda.pl/rtvforum/topic3499254.html
- https://www.elektroda.pl/rtvforum/topic2792620.html
- https://www.elektroda.pl/rtvforum/topic2990515.html

so my thanks goes to these people :)
