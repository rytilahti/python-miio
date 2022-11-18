Push Server
===========

The package provides a push server to act on events from devices,
such as those from Zigbee devices connected to a gateway device.
The server itself acts as a miio device receiving the events it has :ref:`subscribed to receive<events_subscribe>`,
and calling the registered callbacks accordingly.

.. contents:: Contents
   :local:

.. note::

    While the eventing has been so far tested only on gateway devices, other devices that allow scene definitions on the
    mobile app may potentially support this functionality. See :ref:`how to obtain event information<obtain_event_info>` for details
    how to check if your target device supports this functionality.


1. The push server is started and listens for incoming messages (:meth:`PushServer.start`)
2. A miio device and its callback needs to be registered to the push server (:meth:`PushServer.register_miio_device`).
3. A message is sent to the miio device to subscribe a specific event to the push server,
   basically a local scene is made with as target the push server (:meth:`PushServer.subscribe_event`).
4. The device will start keep alive communication with the push server (pings).
5. When the device triggers an event (e.g., a button is pressed),
   the push server gets notified by the device and executes the registered callback.


Events
------

Events are the triggers for a scene in the mobile app.
Most triggers that can be used in the mobile app can be converted to a event that can be registered to the push server.
For example: pressing a button, opening a door-sensor, motion being detected, vibrating a sensor or flipping a cube.
When such a event happens,
the miio device will immediately send a message to to push server,
which will identify the sender and execute its callback function.
The callback function can be used to act on the event,
for instance when motion is detected turn on the light.

Callbacks
---------

Gateway-like devices will have a single callback for all connected Zigbee devices.
The `source_device` argument is set to the device that caused the event e.g. "lumi.123456789abcdef".

Multiple events of the same device can be subscribed to, for instance both opening and closing a door-sensor.
The `action` argument is set to the action e.g., "open" or "close" ,
that was defined in the :class:`PushServer.EventInfo` used for subscribing to the event.

Lastly, the `params` argument provides additional information about the event, if available.

Therefore, the callback functions need to have the following signature:

.. code-block::

    def callback(source_device, action, params):


.. _events_subscribe:

Subscribing to Events
~~~~~~~~~~~~~~~~~~~~~
In order to subscribe to a event a few steps need to be taken,
we assume that a device class has already been initialized to which the events belong:

1. Create a push server instance:

::

    server = PushServer(miio_device.ip)

.. note::

    The server needs an IP address of a real, working miio device as it connects to it to find the IP address to bind on.

2. Start the server:

::

    await push_server.start()

3. Define a callback function:

::

    def callback_func(source_device, action, params):
        _LOGGER.info("callback '%s' from '%s', params: '%s'", action, source_device, params)

4. Register the miio device to the server and its callback function to receive events from this device:

::

    push_server.register_miio_device(miio_device, callback_func)

5. Create an :class:`PushServer.EventInfo` (:ref:`how to obtain event info<obtain_event_info>`)
    object with the event to subscribe to:

::

    event_info = EventInfo(
        action="alarm_triggering",
        extra="[1,19,1,111,[0,1],2,0]",
        trigger_token=miio_device.token,
    )

6. Send a message to the device to subscribe for the event to receive messages on the push_server:

::

    await push_server.subscribe_event(miio_device, event_info)

7. The callback function should now be called whenever a matching event occurs.

8. You should stop the server when you are done with it.
   This will automatically inform all devices with event subscriptions
   to stop sending more events to the server.

::

    await push_server.stop()


.. _obtain_event_info:

Obtaining Event Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you want to support a new type of event in python-miio,
you need to first perform a packet capture of the mobile Xiaomi Home app
to retrieve the necessary information for that event.

1. Prepare your system to capture traffic between the gateway device and your mobile phone. You can, for example, use `BlueStacks emulator <https://www.bluestacks.com>`_ to run the Xiaomi Home app, and `WireShark <https://www.wireshark.org>`_ to capture the network traffic.
2. In the Xiaomi Home app go to `Scene` --> `+` --> for "If" select the device for which you want to make the new event
3. Select the event you want to add
4. For "Then" select the same gateway as the Zigbee device is connected to (or the gateway itself).
5. Select the any action, e.g., "Control nightlight" --> "Switch gateway light color",
   and click the finish checkmark and accept the default name.
6. Repeat the steps 3-5 for all new events you want to implement.
7. After you are done, you can remove the created scenes from the app and stop the traffic capture.
8. You can use `devtools/parse_pcap.py` script to parse the captured PCAP files.

::

    python devtools/parse_pcap.py <pcap file> --token <token of your gateway>


.. note::

    Note, you can repeat `--token` parameter to list all tokens you know to decrypt traffic from all devices:

10. You should now see the decoded communication of between the Xiaomi Home app and your gateway.
11. You should see packets like the following in the output,
    the most important information is stored under the `data` key:

::

    {
        "id" : 1234,
        "method" : "send_data_frame",
        "params" : {
            "cur" : 0,
            "data" : "[[\"x.scene.1234567890\",[\"1.0\",1234567890,[\"0\",{\"src\":\"device\",\"key\":\"event.lumi.sensor_magnet.aq2.open\",\"did\":\"lumi.123456789abcde\",\"model\":\"lumi.sensor_magnet.aq2\",\"token\":\"\",\"extra\":\"[1,6,1,0,[0,1],2,0]\",\"timespan\":[\"0 0 * * 0,1,2,3,4,5,6\",\"0 0 * * 0,1,2,3,4,5,6\"]}],[{\"command\":\"lumi.gateway.v3.set_rgb\",\"did\":\"12345678\",\"extra\":\"[1,19,7,85,[40,123456],0,0]\",\"id\":1,\"ip\":\"192.168.1.IP\",\"model\":\"lumi.gateway.v3\",\"token\":\"encrypted0token0we0need000000000\",\"value\":123456}]]]]",
            "data_tkn" : 12345,
            "total" : 1,
            "type" : "scene"
        }
    }


12. Now, extract the necessary information form the packet capture to create :class:`PushServer.EventInfo` objects.

13. Locate the element containing `"key": "event.*"` in the trace,
    this is the event triggering the command in the trace.
    The `action` of the `EventInfo` is normally the last part of the `key` value, e.g.,
    `open` (from `event.lumi.sensor_magnet.aq2.open`) in the example above.

14. The `extra` parameter is the most important piece containing the event details,
    which you can directly copy from the packet capture.

::

    event_info = EventInfo(
        action="open",
        extra="[1,6,1,0,[0,1],2,0]",
    )


.. note::

    The `action` is an user friendly name of the event, can be set arbitrarily and will be received by the server as the name of the event.
    The `extra` is the identification of the event.

Most times this information will be enough, however the :class:`miio.EventInfo` class allows for additional information.
For example, on Zigbee sub-devices you also need to define `source_sid` and `source_model`,
see :ref:`button press <button_press_example>` for an example.
See the :class:`PushServer.EventInfo` for more detailed documentation.


Examples
--------

Gateway alarm trigger
~~~~~~~~~~~~~~~~~~~~~

The following example shows how to create a push server and make it to listen for alarm triggers from a gateway device.
This is proper async python code that can be executed as a script.


.. literalinclude:: examples/push_server/gateway_alarm_trigger.py
   :language: python



.. _button_press_example:

Button press
~~~~~~~~~~~~

The following examples shows a more complex use case of acting on button presses of Aqara Zigbee button.
Since the source device (the button) differs from the communicating device (the gateway),
some additional parameters are needed for the :class:`PushServer.EventInfo`: `source_sid` and `source_model`.

.. literalinclude:: examples/push_server/gateway_button_press.py
   :language: python


:py:class:`API <miio.push_server>`
