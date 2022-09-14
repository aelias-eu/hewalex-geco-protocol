#!/usr/bin/python3
# Author:      aelias-eu
# Description: Thi simple script will publish data to mqtt so Homeassistant can discover the Hewalex data automatically 
#              (For detailed informations look at MQTT Autodiscovery  https://www.home-assistant.io/docs/mqtt/discovery/   ) 
#
mqttBroker ="127.0.0.1" 				                    # IP addres or DNS name of your MQTT broker
mqttPrefix="homeassistant/sensor/hewalex/"					# MQTT Topic prefix 
uidPrefix="1921683175hew"
import paho.mqtt.client as mqtt 
client = mqtt.Client("HEWALEX")
client.connect(mqttBroker) 
client.publish(mqttPrefix+"T1"+"/config",'{"name": "Solar T1", "unique_id":"'+uidPrefix+'_t1", "unit_of_measurement":"°C", "device_class":"temperature", "state_class":"measurement", "state_topic": "domov/pivnica/solar/hewalex/decoded/T1"}',0,True)
client.publish(mqttPrefix+"T2"+"/config",'{"name": "Solar T2", "unique_id":"'+uidPrefix+'_t2", "unit_of_measurement":"°C", "device_class":"temperature", "state_class":"measurement", "state_topic": "domov/pivnica/solar/hewalex/decoded/T2"}',0,True)
client.publish(mqttPrefix+"T3"+"/config",'{"name": "Solar T3", "unique_id":"'+uidPrefix+'_t3", "unit_of_measurement":"°C", "device_class":"temperature", "state_class":"measurement", "state_topic": "domov/pivnica/solar/hewalex/decoded/T3"}',0,True)
client.publish(mqttPrefix+"T4"+"/config",'{"name": "Solar T4", "unique_id":"'+uidPrefix+'_t4", "unit_of_measurement":"°C", "device_class":"temperature", "state_class":"measurement", "state_topic": "domov/pivnica/solar/hewalex/decoded/T4"}',0,True)
client.publish(mqttPrefix+"T5"+"/config",'{"name": "Solar T5", "unique_id":"'+uidPrefix+'_t5", "unit_of_measurement":"°C", "device_class":"temperature", "state_class":"measurement", "state_topic": "domov/pivnica/solar/hewalex/decoded/T5"}',0,True)
client.publish(mqttPrefix+"T6"+"/config",'{"name": "Solar T6", "unique_id":"'+uidPrefix+'_t6", "unit_of_measurement":"°C", "device_class":"temperature", "state_class":"measurement", "state_topic": "domov/pivnica/solar/hewalex/decoded/T6"}',0,True)
client.publish(mqttPrefix+"SolarPower"+"/config",'{"name": "Solar Power", "unique_id":"'+uidPrefix+'_spower", "unit_of_measurement":"kW","state_class":"measurement", "device_class":"power","state_topic": "domov/pivnica/solar/hewalex/decoded/SolarPower"}',0,True)
client.publish(mqttPrefix+"CollectorPumpOn"+"/config",'{"name": "Solar CollectorPumpOn", "unique_id":"'+uidPrefix+'_colectorpump","state_topic": "domov/pivnica/solar/hewalex/decoded/CollectorPumpON"}',0,True)
client.publish(mqttPrefix+"Flow"+"/config",'{"name": "Solar CollectorFluidFlow",  "unique_id":"'+uidPrefix+'_fluidflow","unit_of_measurement":"l/min","state_topic": "domov/pivnica/solar/hewalex/decoded/Flow"}',0,True)
client.publish(mqttPrefix+"TotalEnergy"+"/config",'{"name": "Solar TotalEnergy", "unique_id":"'+uidPrefix+'_totalenergy", "unit_of_measurement":"kWh","state_class":"total_increasing", "device_class":"energy","state_topic": "domov/pivnica/solar/hewalex/decoded/TotalEnergy"}',0,True)
client.publish(mqttPrefix+"DO"+"/config",'{"name": "Solar DO", "unique_id":"'+uidPrefix+'_do","state_topic": "domov/pivnica/solar/hewalex/decoded/DigitalOUT"}',0,True)
client.publish(mqttPrefix+"PowerConsumption"+"/config",'{"name": "Solar Power Consumption", "unique_id":"'+uidPrefix+'_powerconsumption","unit_of_measurement":"kW", "device_class":"power", "state_class":"measurement","state_topic": "domov/pivnica/solar/hewalex/decoded/PowerConsumption"}',0,True)
client.publish(mqttPrefix+"PumpSpeed"+"/config",'{"name": "Solar PumpSpeed", "unique_id":"'+uidPrefix+'_pumpspeed","state_topic": "domov/pivnica/solar/hewalex/decoded/PumpSpeed"}',0,True)
