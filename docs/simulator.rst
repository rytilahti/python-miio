Device Simulators
*****************

This section describes how to use and develop device simulators that can be useful when
developing either this library and its CLI tool, as well as when developing applications
communicating with MiIO/MiOT devices, like the Home Assistant integration, even when you
have no access to real devices.

.. contents:: Contents
   :local:


MiIO Simulator
--------------

The ``miiocli devtools miio-simulator`` command can be used to simulate devices.
You can command the simulated devices using the ``miiocli`` tool or any other implementation
that talks the MiIO protocol, like `Home Assistant <https://www.home-assistant.io>`_.

Behind the scenes, the simulator uses :class:`the push server <miio.push_server.server.PushServer>` to
handle the low-level protocol handling.
To make it easy to simulate devices, it uses YAML-based :ref:`device description files <miio_device_descriptions>`
to describe information like models and exposed properties to simulate.

.. note::

    The simulator currently supports only devices whose properties are queried using ``get_prop`` method,
    and whose properties are set using a single setter method (e.g., ``set_fan_speed``) accepting the new value.


Usage
"""""

You start the simulator like this::

    miiocli devtools miio-simulator --file miio/integrations/fan/zhimi/zhimi_fan.yaml

The mandatory ``--file`` option takes a path to :ref:`a device description file <miio_device_descriptions>` file
that defines information about the device to be simulated.

.. note::

    You can define ``--model`` to define which model string you want to expose to the clients.
    The MAC address of the device is generated from the model string, making them unique for
    downstream use cases, e.g., to make them distinguishable to Home Assistant.

After the simulator has started, you can communicate with it using the ``miiocli``::

    $ export MIIO_FAN_TOKEN=00000000000000000000000000000000

    $ miiocli fan --host 127.0.0.1 info

    Model: zhimi.fan.sa1
    Hardware version: MW300
    Firmware version: 1.2.4_16

    $ miiocli fan --ip 127.0.0.1 status

    Power: on
    Battery: None %
    AC power: True
    Temperature: None °C
    Humidity: None %
    LED: None
    LED brightness: LedBrightness.Bright
    Buzzer: False
    Child lock: False
    Speed: 277
    Natural speed: 2
    Direct speed: 1
    Oscillate: False
    Power-off time: 12
    Angle: 120


.. note::

    The default token is hardcoded to full of zeros (``00000000000000000000000000000000``).
    We defined ``MIIO_FAN_TOKEN`` to avoid repeating ``--token`` for each command.

.. note::

    Although Home Assistant uses MAC address as a unique ID to identify the device, the model information
    is stored in the configuration entry which is used to initialize the integration.

    Therefore, if you are testing multiple simulated devices in Home Assistant, you want to disable other simulated
    integrations inside Home Assistant to avoid them being updated against a wrong simulated device.

.. _miio_device_descriptions:

Device Descriptions
"""""""""""""""""""

The simulator uses YAML files that describe information about the device, including supported models
and the available properties.

Required Information
~~~~~~~~~~~~~~~~~~~~

The file begins with a definition of models supported by the file:

.. code-block:: yaml

    models:
      - name: Name of the device, if known
        model: model.string.v2
      - model: model.string.v3

You need to have ``model`` for each model the description file wants to support.
The name is not required, but recommended.
This information is currently used to set the model information for the simulated
device when not overridden using the ``--model`` option.

The description file can define a list of *properties* the device supports for ``get_prop`` queries.
You need to define several mappings for each property:

    * ``name`` defines the name used for fetching using the ``get_prop`` request
    * ``type`` defines the type of the property, e.g., ``bool``, ``int``, or ``str``
    * ``value`` is the value which is returned for ``get_prop`` requests
    * ``setter`` defines the method that allows changing the ``value``
    * ``models`` list, if the property is only available on some of the supported models

.. note::

    The schema might change in the future to accommodate other potential uses, e.g., allowing
    definition of new files using pure YAML without a need for Python implementation.
    Refer :ref:`example_desc` for a complete, working example.

Alternatively, you can define *methods* with their responses by defining ``methods``, which is necessary to simulate
devices that use other ways to obtain the status information (e.g., on Roborock vacuums).
You can either use ``result`` or ``result_json`` to define the response for the given method:

.. code-block:: yaml

    methods:
      - name: get_status
        result:
          - some_variable: 1
            another_variable: "foo"
      - name: get_timezone
        result_json: '["UTC"]'

Calling method ``get_status`` will return ``[{"some_variable": 1, "another_variable": "foo"}]``,
the ``result_json`` will be parsed and serialized to ``["UTC"]`` when sent to the client.
A full working example can be found in :ref:`example_desc_methods`.


Minimal Working Example
~~~~~~~~~~~~~~~~~~~~~~~

The following YAML file defines a very minimal device having a single model with two properties,
and exposing also a custom method (``reboot``):

.. code-block:: yaml

    models:
      - name: Some Fan
        model: some.fan.model
    properties:
      - name: speed
        type: int
        value: 33
        setter: set_speed
      - name: is_on
        type: bool
        value: false
    methods:
      - name: reboot
        result_json: '["ok"]'

In this case, the ``get_prop`` method call with parameters ``['speed', 'is_on']`` will return ``[33, 0]``.
The ``speed`` property can be changed by calling the ``set_speed`` method.
See :ref:`example_desc` for a more complete example.

.. _example_desc:

Example Description File
~~~~~~~~~~~~~~~~~~~~~~~~

The following description file shows a complete,
concrete example for a device using ``get_prop`` for accessing the properties (``zhimi_fan.yaml``):

.. literalinclude:: ../miio/integrations/fan/zhimi/zhimi_fan.yaml
   :language: yaml

.. _example_desc_methods:

Example Description File Using Methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following description file (``simulated_roborock.yaml``) shows a complete,
concrete example for a device using custom method names for obtaining the status.

.. literalinclude:: ../miio/integrations/vacuum/roborock/simulated_roborock.yaml
   :language: yaml


MiOT Simulator
--------------

.. note:: TBD.
