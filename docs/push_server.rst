Push Server
===========

The package provides a dummy push server to act on events from devices,
such as those from Zigbee devices connected to a gateway device.
The server itself acts as a miio device receiving the events it has :ref:`subscribed to receive<events_subscribe>`,
and calling the registered callbacks accordingly.

.. note::

    While the eventing has been so far tested only on gateway devices, other devices that allow scene definitions on the
    mobile app may potentially support this functionality. See :ref:`how to obtain event information<events_obtain>` for details
    how to check if your target device supports this functionality.


1. The push server registers itself as a scene target for specific event data
2. When the device triggers an event, the push server gets notified and executes the registered callback
3. ...? This is just an example, but it would be great to have a high-level,
   step-wise description how the eventing works

.. todo::

    Besides describing here how the event system works in the background,
    maybe it makes sense to describe the elements (the subsections below) using
    a tutorial like example?


Events
------

.. todo::

    add short description on what events are, how they work, and how they work (internally, using scenes..?) in the context of the server.


.. _events_obtain:

Obtaining Event Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo::

    Describe how to obtain the necessary information from packet traces


.. _events_subscribe:

Subscribing to Events
~~~~~~~~~~~~~~~~~~~~~

.. code-block::

    Here's just a short example how to register for specific events,
    including the construction of EventInfo objects and description of necessary information?



Examples
--------

Gateway alarm trigger
~~~~~~~~~~~~~~~~~~~~~

The following example shows how to create a push server and make it to listen for alarm triggers from a gateway device.

.. todo:: describe


.. literalinclude:: examples/push_server/gateway_alarm_trigger.py
   :language: python



Button press
~~~~~~~~~~~~

The following examples shows a more complex use case of acting on button presses of Aqara Zigbee button.

.. todo:: describe how does this differ from the "simple" example

.. literalinclude:: examples/push_server/gateway_button_press.py
   :language: python

:py:class:`API <miio.push_server>`
