Push Server
===========

The package provides a push server to act on events from devices,
such as those from Zigbee devices connected to a gateway device.
The server itself acts as a miio device receiving the events it has :ref:`subscribed to receive<events_subscribe>`,
and calling the registered callbacks accordingly.

.. note::

    While the eventing has been so far tested only on gateway devices, other devices that allow scene definitions on the
    mobile app may potentially support this functionality. See :ref:`how to obtain event information<events_obtain>` for details
    how to check if your target device supports this functionality.


1. The push server is started and listens for incommming messages (server.start)
2. A miio device is registed to the push server where a callback is specified such that the push server will recognize the device (server.register_miio_device).
3. A message is sent to the miio device to subscribe a specific event to the push server, basically a local scene is made with as target the push server (server.subscribe_event).
4. The miio device will start keep alive communication with the push server (pings)
5. When the device triggers an event (eg. a button is pressed), the push server gets notified by the miio device and executes the registered callback


Events
------

Events are the triggers of a scene in the mobile app.
Most triggers that can be used in the mobile app can be converted to a event that can be registered to the push server.
For example: pressing a button, opening a door-sensor, motion beeing detected, vibrating a sensor or flipping a cube.
When such a event happens the miio device will imediatly send a message to to push server that will identify the sending device and execute its callback function.
The callback function can be used to act on the event, for instance when motion is detected turn on the light.

Callbacks
------
Multiple events of the same device can be subscribed to, for instance both opening and closing a door-sensor.
Therefore the callback function has a 'action' parameter that will specify which event triggered the callback: 'open' or 'close'.
Gateway like devices will have a single callback for all there connected zigbee devices.
Therfore the callback function has a 'source_device' paramter specifying the source of the event which indicates the zigbee device that sent the message.
At last the callback also has a 'params' parameter providing aditional information about the event in case that is supported.
Callback functions therefore need to have the following form:
.. code-block::
    def callback(source_device, action, params):

.. _events_subscribe:

Subscribing to Events
~~~~~~~~~~~~~~~~~~~~~
In order to subscribe to a event a few steps need to be taken, we assume a miio_device class has already been intialized to which the events belong:
1. Create the push server
server = PushServer(miio_device.ip)  # A ip of a real working miio_device needs to be specified, it does not matter which device.
2. Start the server
await push_server.start()
3. Define a callback function
def callback_func(source_device, action, params):
    _LOGGER.info("callback '%s' from '%s', params: '%s'", action, source_device, params)
4. Register the miio device to the server and its callback function to receive events for this device
push_server.register_miio_device(miio_device, callback_func)
5. Create a EventInfo object with the information about the event you which to subscribe to (:ref:`Obtain event info<obtain_event_info>`)
event_info = EventInfo(
    action="alarm_triggering",
    extra="[1,19,1,111,[0,1],2,0]",
    trigger_token=miio_device.token,
)
6. Send a message to the miio_device to subscribe for the event to receive messages on the push_server
push_server.subscribe_event(miio_device, event_info)
7. Now you will see the callback function beeing called whenever the event occurs
await asyncio.sleep(30)
8. When done stop the push_server, this will send messages to all subscribed miio_devices to unsubscribe all events
push_server.stop()

.. _obtain_event_info:

Obtaining Event Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you want to support a new type of event in python-miio, a packet capture of the mobile Xiaomi Home app of that event is needed to retrieve the necessary information.
To do this you will need 4 programs running on a PC:
 - [BlueStacks](https://www.bluestacks.com) to emulate the Xiaomi Home app on windows
 - [WireShark](https://www.wireshark.org) to capture the network packets send by the Xiaomi Home app in BlueStacks
 - [Python](https://www.python.org/downloads/) at least version 3.9 is required
 - [Python-miio devtools](https://github.com/rytilahti/python-miio/tree/master/devtools) to decode the captured packets of WireShark

1. Install BlueStacks and WireShark and [download the latest python-miio](https://github.com/rytilahti/python-miio) (green Code button --> download ZIP, then unzip on your computer).
2. Set up Xiaomi Home app in BlueStacks and login to synchronize devices.
3. Open WireShark, select all your interfaces, apply a filter "ip.src==192.168.1.GATEWAY_IP or ip.dst==192.168.1.GATEWAY_IP" in which GATEWAY_IP is the Ip-address of your gateway, and start capturing packets
4. In the Xiaomi Home app go to `scene` --> `+` --> for "If" select the device for which you want to make the new Event --> select the event you want to support --> for "Then" select the same gateway as the zigbee device is connected to (or the gateway itself) --> select "Control nightlight" --> select "Switch gateway light color" --> click the finish checkmark and accept the default name.
5. Repeat step 4 for all new Events you want to implement.
6. Stop capturing packets in WireShark, you can now delete the `scenes` again you just created in the Xiaomi Home app.
7. In WireShark go to `file` --> `Save as` --> select `pcap` instead of `pcapng` under `save as type` --> save the file on your computer
8. Get the regular token of your gateway from the Home Assistant `core.config_entries` file located in your `config\.storage` folder of Home Assistant (search for `"domain": "xiaomi_miio"`)
9. open a command line --> `python3 C:\path\to\python-miio\folder\step1\devtools\parse_pcap.py C:\path\to\the\file\you\just\saved\filename.pcap --token TokenTokenToken` in which you will need to fill in the paths and the token, optionally multiple tokens can be added by repeating `--token Token2Token2Token2`.
10. You schould now see the decoded communication of the Xiaomi Home app to your gateway and back during the packet capture.
11. One of the packets schould look something like this:
```{"id":1234,"method":"send_data_frame","params":{"cur":0,"data":"[[\"x.scene.1234567890\",[\"1.0\",1234567890,[\"0\",{\"src\":\"device\",\"key\":\"event.lumi.sensor_magnet.aq2.open\",\"did\":\"lumi.123456789abcde\",\"model\":\"lumi.sensor_magnet.aq2\",\"token\":\"\",\"extra\":\"[1,6,1,0,[0,1],2,0]\",\"timespan\":[\"0 0 * * 0,1,2,3,4,5,6\",\"0 0 * * 0,1,2,3,4,5,6\"]}],[{\"command\":\"lumi.gateway.v3.set_rgb\",\"did\":\"12345678\",\"extra\":\"[1,19,7,85,[40,123456],0,0]\",\"id\":1,\"ip\":\"192.168.1.IP\",\"model\":\"lumi.gateway.v3\",\"token\":\"encrypted0token0we0need000000000\",\"value\":123456}]]]]","data_tkn":12345,"total":1,"type":"scene"}}```
12. Now extract the necessary information form the packet capture:
```
    event_info = EventInfo(
        action="open",  # user friendly name of the event, can be set arbitrarily and will be received by the server as the name of the event
        extra="[1,6,1,0,[0,1],2,0]",  # the identification of this event, this determines on what event the callback is triggered
    )
```
The 'action' is normally taken equal to the last part of the "key" in the packet capture.
So `\"key\":\"event.lumi.sensor_magnet.aq2.open\"` becomes 'open'
The 'extra' paramter is the most importatant and is directly coppied from the packet caputure.
Note that you need to take the first 'extra' parameter in the capture that represents the trigger/event.
The second 'extra' parameter in the capture represents the action, in this case turning on the gateway light, however this will be replaced by a action to notify the push server automatically and is therefore not needed.

Most times this information will be enough, however the EventInfo class allows for aditional information:
```
    event_info = EventInfo(
        action="open",  # user friendly name of the event, can be set arbitrarily and will be received by the server as the name of the event
        extra="[1,6,1,0,[0,1],2,0]",  # the identification of this event, this determines on what event the callback is triggered
        event: "open"  # defaults to the action
        command_extra="[1,19,7,85,[40,123456],0,0]"  # will be received by the push server, hopefully this will allow us to obtain extra information about the event for instance the vibration intesisty or light level that triggered the event (still experimental)
        trigger_value: # defautls to None, only needed if the trigger has a certain threshold value (like a temperature for a wheather sensor), a "value" key will be present in the first part of the capture.
        trigger_token: ""   # defaults to "", only needed for protected events like the alarm feature of a gateway, equal to the "token" of the first part of the caputure.
        source_sid: Optional[str] = None  # Normally automatically obtained from the device, only needed for zigbee devices: the "did" key
        source_model: Optional[str] = None  # Normally not needed and obtained from device, only needed for zigbee devices: the "model" key
    )
```

You might need to repeat the packet capture again if it did not show up the first time, if it still does not show up, make sure you do not have a VPN enabled while executing steps 3 to 6 and make sure you use the correct token for decoding the packets (each gateway has its own token).


Examples
--------

Gateway alarm trigger
~~~~~~~~~~~~~~~~~~~~~

The following example shows how to create a push server and make it to listen for alarm triggers from a gateway device.
This is proper async python code that can be executed as a script. 


.. literalinclude:: examples/push_server/gateway_alarm_trigger.py
   :language: python



Button press
~~~~~~~~~~~~

The following examples shows a more complex use case of acting on button presses of Aqara Zigbee button.
Since the source device (the button) differs from the communicating device (the gateway) some aditional EventInfo is needed: source_sid and source_model.

.. literalinclude:: examples/push_server/gateway_button_press.py
   :language: python

:py:class:`API <miio.push_server>`
