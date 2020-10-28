# hewalex-geco-protocol
Communication tool for GECO G-422 range of solar pump controllers, used also (but not only) in the Hewalex ZPS-18e 

The **hewalex2mqtt.py** script will connect to the hewalex controller, request registers 100-250 and publish data to the MQTT broker.
You have to edit settings directly in the script.
Requests are hardcoded (asuming the controller's physical and also logical address is 2) so if you need to change them, you have to recalculate the CRC. 
I take it as working PoC. Currently I'm running it in cron from my armbian-based device and processing actual temperatures via MQTT to homeassistant.

It is possible to send configuration data to the controller, but I don't have the communication device for Ekontrol connection - this would require some sniffing on such installation. 

If you look at the demo of Ekontrol by Hewalex ( https://ekontrol.pl/en/33570/scheme/ ), you can see pretty much what can be done with this system. They dont' seem to have any public API for the Ekontrol interface, so there is that...

This work is inspired & based on informations provided on the elektroda.pl forum 
- https://www.elektroda.pl/rtvforum/topic3499254.html
- https://www.elektroda.pl/rtvforum/topic2792620.html
- https://www.elektroda.pl/rtvforum/topic2990515.html

so my thanks goes to these people :)
