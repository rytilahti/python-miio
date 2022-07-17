Gateway
=======

Adding support for new Zigbee devices
-------------------------------------

Once the event information is obtained as :ref:`described in the push server docs<obtain_event_info>`,
a new event for a Zigbee device connected to a gateway can be implemented as follows:

1. Open `miio/gateway/devices/subdevices.yaml` file and search for the target device for the new event.
2. Add an entry for the new event:

.. code-block:: yaml

    properties:
      - property: is_open # the new property of this device (optional)
        default: False    # default value of the property when the device is initialized (optional)
    push_properties:
      open:               # the event you added, see the decoded packet capture `\"key\":\"event.lumi.sensor_magnet.aq2.open\"` take this equal to everything after the model
        property: is_open # the property as listed above that this event will link to (optional)
        value: True       # the value the property as listed above will be set to if this event is received (optional)
        extra: "[1,6,1,0,[0,1],2,0]"  # the identification of this event, see the decoded packet capture `\"extra\":\"[1,6,1,0,[0,1],2,0]\"`
      close:
        property: is_open
        value: False
        extra: "[1,6,1,0,[0,0],2,0]"

3. Create a pull request to get the event added to this library.
