# Gateway and zigbee devices

## Supporting new push actions

To support new push actions or properties a packet capture of the Xiaomi Home app needs to be made to figure out the required data.
To do this you will need 4 programs running on a PC:
 - [BlueStacks](https://www.bluestacks.com) to emulate the Xiaomi Home app on windows
 - [WireShark](https://www.wireshark.org) to capture the network packets send by the Xiaomi Home app in BlueStacks
 - [Python](https://www.python.org/downloads/) at least version 3.9 is required
 - [Python-miio devtools](https://github.com/rytilahti/python-miio/tree/master/devtools) to decode the captured packets of WireShark

1. Install BlueStacks and WireShark and [download the latest python-miio](https://github.com/rytilahti/python-miio) (green Code button --> download ZIP, then unzip on your computer).
2. Set up Xiaomi Home app in BlueStacks and login to synchronize devices.
3. Open WireShark, select all your interfaces, apply a filter "ip.src==192.168.1.GATEWAY_IP or ip.dst==192.168.1.GATEWAY_IP" in which GATEWAY_IP is the Ip-address of your gateway, and start capturing packets
4. In the Xiaomi Home app go to `scene` --> `+` --> for "If" select the device for which you want to make the new push action --> select the action you want to support --> for "Then" select the same gateway as the zigbee device is connected to (or the gateway itself) --> select "Control nightlight" --> select "Switch gateway light color" --> click the finish checkmark and accept the default name.
5. Repeat step 4 for all new push actions you want to implement.
6. Stop capturing packets in WireShark, you can now delete the `scenes` again you just created in the Xiaomi Home app.
7. In WireShark go to `file` --> `Save as` --> select `pcap` instead of `pcapng` under `save as type` --> save the file on your computer
8. Get the regular token of your gateway from the Home Assistant `core.config_entries` file located in your `config\.storage` folder of Home Assistant (search for `"domain": "xiaomi_miio"`)
9. open a command line --> `python3 C:\path\to\python-miio\folder\step1\devtools\parse_pcap.py C:\path\to\the\file\you\just\saved\filename.pcap --token TokenTokenToken` in which you will need to fill in the paths and the token, optionally multiple tokens can be added by repeating `--token Token2Token2Token2`.
10. You schould now see the decoded communication of the Xiaomi Home app to your gateway and back during the packet capture.
11. One of the packets schould look something like this:
```{"id":1234,"method":"send_data_frame","params":{"cur":0,"data":"[[\"x.scene.1234567890\",[\"1.0\",1234567890,[\"0\",{\"src\":\"device\",\"key\":\"event.lumi.sensor_magnet.aq2.open\",\"did\":\"lumi.123456789abcde\",\"model\":\"lumi.sensor_magnet.aq2\",\"token\":\"\",\"extra\":\"[1,6,1,0,[0,1],2,0]\",\"timespan\":[\"0 0 * * 0,1,2,3,4,5,6\",\"0 0 * * 0,1,2,3,4,5,6\"]}],[{\"command\":\"lumi.gateway.v3.set_rgb\",\"did\":\"12345678\",\"extra\":\"[1,19,7,85,[40,123456],0,0]\",\"id\":1,\"ip\":\"192.168.1.IP\",\"model\":\"lumi.gateway.v3\",\"token\":\"encrypted0token0we0need000000000\",\"value\":123456}]]]]","data_tkn":12345,"total":1,"type":"scene"}}```
13. go to the miio\gateway\devices\subdevices.YAML file of this python module and search for the device you want to implement the action for.
14. Add the action you just discoved like this:
```
  properties:
    - property: is_open # the new property of this device (optional)
      default: False    # default value of the property when the device is initialized (optional)
  push_properties:
    open:               # the action you added, see the decoded packet capture `\"key\":\"event.lumi.sensor_magnet.aq2.open\"` take this equal to everything after the model
      property: is_open # the property as listed above that this action will link to (optional)
      value: True       # the value the property as listed above will be set to if this action is received (optional)
      extra: "[1,6,1,0,[0,1],2,0]"  # the identification of this action, see the decoded packet capture `\"extra\":\"[1,6,1,0,[0,1],2,0]\"`
    close:
      property: is_open
      value: False
      extra: "[1,6,1,0,[0,0],2,0]"
```
14. Make a Pull Request to include the new action to this python module.


You might need to repeat the packet capture again if it did not show up the first time, if it still does not show up, make sure you do not have a VPN enabled while executing steps 3 to 6 and make sure you use the correct token for decoding the packets (each gateway has its own token).
