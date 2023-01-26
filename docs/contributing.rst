Contributing
************

Contributions of any sort are more than welcome,
so we hope this short introduction will help you to get started!
Shortly put: we use black_ to format our code, isort_ to sort our imports, pytest_ to test our code,
flake8_ to do its checks, and doc8_ for documentation checks.

See :ref:`devenv` for setting up a development environment,
and :ref:`new_devices` for some helpful tips for adding support for new devices.

.. contents:: Contents
   :local:


.. _devenv:

Development environment
-----------------------

This section will shortly go through how to get you started with a working development environment.
We use `poetry <https://python-poetry.org/>`__ for managing the dependencies and packaging, so simply execute::

    poetry install

If you were not already inside a virtual environment during the install,
poetry will create one for you.
You can execute commands inside this environment by using ``poetry run <command>``,
or alternatively,
enter the virtual environment shell by executing ``poetry shell`` to avoid repeating ``poetry run``.

To verify the installation, you can launch tox_ to run all the checks::

    tox

In order to make feedback loops faster, we automate our code checks by using precommit_ hooks.
Therefore the first step after setting up the development environment is to install them::

    pre-commit install

You can always `execute the checks <#code-checks>`_ also without doing a commit.


.. _linting:

Code checks
~~~~~~~~~~~

Instead of running all available checks during development,
it is also possible to execute only the code checks by calling.
This will execute the same checks that would be done automatically by precommit_ when you make a commit::

    tox -e lint


.. _tests:

Tests
~~~~~

We prefer to have tests for our code, so we use pytest_ you can also use by executing::

    pytest miio

When adding support for a new device or extending an already existing one,
please do not forget to create tests for your code.

Generating documentation
~~~~~~~~~~~~~~~~~~~~~~~~

You can compile the documentation and open it locally in your browser::

    sphinx-build docs/ generated_docs
    $BROWSER generated_docs/index.html

Replace `$BROWSER` with your preferred browser, if the environment variable is not set.


.. _new_devices:

Improving device support
------------------------

Whether adding support for a new device or improving an existing one,
the journey begins by finding out the commands used to control the device.
This usually involves capturing packet traces between the device and the official app,
and analyzing those packet traces afterwards.

Traffic Capturing
~~~~~~~~~~~~~~~~~

The process is as follows:

1. Install Android emulator (`BlueStacks emulator <https://www.bluestacks.com>`_ has been reported to work on Windows).
2. Install the official Mi Home app in the emulator and set it up to use your device.
3. Install `WireShark <https://www.wireshark.org>`_ (or use ``tcpdump`` on Linux) to capture the device traffic.
4. Use the app to control the device and save the resulting PCAP file for later analyses.
5. :ref:`Obtain the device token<obtaining_tokens>` in order to decrypt the traffic.
6. Use ``miiocli devtools parse-pcap`` script to parse the captured PCAP files.

.. note::

    You can pass as many tokens you want to ``parse-pcap``, they will be tested sequentially until decryption succeeds,
    or the input list is exhausted.

::

    $ miiocli devtools parse-pcap captured_traffic.pcap <token> <another_token>

    host   -> strip {'id': 6489, 'method': 'get_prop', 'params': ['power', 'temperature', 'current', 'mode', 'power_consume_rate', 'wifi_led', 'power_price']}
    strip  -> host   {'result': ['on', 48.91, 0.07, None, 7.69, 'off', 999], 'id': 6489}
    host   -> vacuum {'id': 8606, 'method': 'get_status', 'params': []}
    vacuum -> host   {'result': [{'msg_ver': 8, 'msg_seq': 10146, 'state': 8, 'battery': 100, 'clean_time': 966, 'clean_area': 19342500, 'error_code': 0, 'map_present': 1, 'in_cleaning': 0, 'fan_power': 60, 'dnd_enabled': 1}], 'id': 8606}

    ...

    == stats ==
            miio_packets: 24
            results: 12

    == dst_addr ==
        ...
    == src_addr ==
        ...

    == commands ==
            get_prop: 3
            get_status: 3
            set_custom_mode: 2
            set_wifi_led: 2
            set_power: 2


Testing Properties
~~~~~~~~~~~~~~~~~~

Another option for MiIO devices is to try to test which property accesses return a response.
Some ideas about the naming of properties can be located from the existing integrations.

The ``miiocli devtools test-properties`` command can be used to perform this testing:

.. code-block::

    $ miiocli devtools test-properties power temperature current mode power_consume_rate voltage power_factor elec_leakage

    Testing properties ('power', 'temperature', 'current', 'mode', 'power_consume_rate', 'voltage', 'power_factor', 'elec_leakage') for zimi.powerstrip.v2
    Testing power                'on' <class 'str'>
    Testing temperature          49.13 <class 'float'>
    Testing current              0.07 <class 'float'>
    Testing mode                 None
    Testing power_consume_rate   7.8 <class 'float'>
    Testing voltage              None
    Testing power_factor         0.0 <class 'float'>
    Testing elec_leakage         None
    Found 5 valid properties, testing max_properties..
    Testing 5 properties at once (power temperature current power_consume_rate power_factor): OK for 5 properties

    Please copy the results below to your report
    ### Results ###
    Model: zimi.powerstrip.v2
    Total responsives: 5
    Total non-empty: 5
    All non-empty properties:
    {'current': 0.07,
     'power': 'on',
     'power_consume_rate': 7.8,
     'power_factor': 0.0,
     'temperature': 49.13}
    Max properties: 5



.. _miot:

MiOT devices
~~~~~~~~~~~~

For MiOT devices it is possible to obtain the available commands from the cloud.
The git repository contains a script, ``devtools/miottemplate.py``, that allows both
downloading the description files and parsing them into more understandable form.


.. _checklist:

Development checklist
---------------------

1. All device classes are derived from either :class:`~miio.device.Device` (for MiIO)
   or :class:`~miio.miot_device.MiotDevice` (for MiOT) (:ref:`minimal_example`).
2. All commands and their arguments should be decorated with :meth:`@command <miio.click_common.command>` decorator,
   which will make them accessible to `miiocli` (:ref:`miiocli`).
3. All implementations must either include a model-keyed :obj:`~miio.device.Device._mappings` list (for MiOT),
   or define :obj:`~miio.device.Device._supported_models` variable in the class (for MiIO).
   listing the known models (as reported by :meth:`~miio.device.Device.info()`).
4. Status containers is derived from :class:`~miio.devicestatus.DeviceStatus` class and all properties should
   have type annotations for their return values. The information that should be exposed directly
   to end users should be decorated using appropriate decorators (e.g., `@sensor` or `@setting`) to make
   them discoverable (:ref:`status_containers`).
5. Add tests at least for the status container handling (:ref:`adding_tests`).
6. Updating documentation is generally not needed as the API documentation
   will be generated automatically.


.. _minimal_example:

Minimal example
~~~~~~~~~~~~~~~

.. TODO::
    Add or link to an example.


.. _miiocli:

miiocli integration
~~~~~~~~~~~~~~~~~~~

All user-exposed methods of the device class should be decorated with
:meth:`miio.click_common.command` to provide console interface.
The decorated methods will be exposed as click_ commands for the given module.
For example, the following definition:

.. code-block:: python

   @command(
       click.argument("string_argument", type=str),
       click.argument("int_argument", type=int, required=False)
   )
   def command(string_argument: str, int_argument: int):
       click.echo(f"Got {string_argument} and {int_argument}")

Produces a command ``miiocli example`` command requiring an argument
that is passed to the method as string, and an optional integer argument.


.. _status_containers:

Status containers
~~~~~~~~~~~~~~~~~

The status container (returned by the :meth:`~miio.device.Device.status` method of the device class)
is the main way for library users to access properties exposed by the device.
The status container should inherit :class:`~miio.devicestatus.DeviceStatus`.
Doing so ensures that a developer-friendly :meth:`~miio.devicestatus.DeviceStatus.__repr__` based on the defined
properties is there to help with debugging.
Furthermore, it allows defining meta information about properties that are especially interesting for end users.
The ``miiocli`` tool will automatically use the defined information to generate a user-friendly output.

.. note::

    The helper decorators are just syntactic sugar to create the corresponding descriptor classes
    and binding them to the status class.

.. note::

    The descriptors are merely hints to downstream users about the device capabilities.
    In practice this means that neither the input nor the output values of functions decorated with
    the descriptors are enforced automatically by this library.

Embedding Containers
""""""""""""""""""""

Sometimes your device requires multiple I/O requests to gather information you want to expose
to downstream users. One example of such is Roborock vacuum integration, where the status request
does not report on information about consumables.

To make it easy for downstream users, you can *embed* other status container classes into a single
one using :meth:`miio.devicestatus.DeviceStatus.embed`.
This will create a copy of the exposed descriptors to the main container and act as a proxy to give
access to the properties of embedded containers.


Sensors
"""""""

Use :meth:`@sensor <miio.devicestatus.sensor>` to create :class:`~miio.descriptors.SensorDescriptor`
objects for the status container.
This will make all decorated sensors accessible through :meth:`~miio.device.Device.sensors` for downstream users.

.. code-block:: python

    @property
    @sensor(name="Voltage", unit="V", some_kwarg_for_downstream="hi there")
    def voltage(self) -> Optional[float]:
        """Return the voltage, if available."""

.. note::

    All keywords arguments not defined in the decorator signature will be available
    through the :attr:`~miio.descriptors.SensorDescriptor.extras` variable.

    This information can be used to pass information to the downstream users,
    see the source of :class:`miio.powerstrip.PowerStripStatus` for example of how to pass
    device class information to Home Assistant.


Settings
""""""""

Use :meth:`@setting <miio.devicestatus.setting>` to create :meth:`~miio.descriptors.SettingDescriptor` objects.
This will make all decorated settings accessible through :meth:`~miio.device.Device.settings` for downstream users.

The type of the descriptor depends on the input parameters:

    * Passing *min_value* or *max_value* will create a :class:`~miio.descriptors.NumberSettingDescriptor`,
      which is useful for presenting ranges of values.
    * Passing an :class:`enum.Enum` object using *choices* will create a
      :class:`~miio.descriptors.EnumSettingDescriptor`, which is useful for presenting a fixed set of options.
    * Otherwise, the setting is considered to be boolean switch.


You can either use *setter* to define a callable that can be used to adjust the value of the property,
or alternatively define *setter_name* which will be used to bind the method during the initialization
to the the :meth:`~miio.descriptors.SettingDescriptor.setter` callable.

Numerical Settings
^^^^^^^^^^^^^^^^^^

The number descriptor allows defining a range of values and information about the steps.
*range_attribute* can be used to define an attribute that is used to read the definitions,
which is useful when the values depend on a device model.

.. code-block::

    class ExampleStatus(DeviceStatus):

        @property
        @setting(name="Color temperature", range_attribute="color_temperature_range")
        def colortemp(): ...

    class ExampleDevice(Device):
        def color_temperature_range() -> ValidSettingRange:
            return ValidSettingRange(0, 100, 5)

Alternatively, *min_value*, *max_value*, and *step* can be used.
The *max_value* is the only mandatory parameter. If not given, *min_value* defaults to ``0`` and *step* to ``1``.

.. code-block::

    @property
    @setting(name="Fan Speed", min_value=0, max_value=100, step=5, setter_name="set_fan_speed")
    def fan_speed(self) -> int:
        """Return the current fan speed."""


Enum-based Settings
^^^^^^^^^^^^^^^^^^^

If the device has a setting with some pre-defined values, you want to use this.

.. code-block::

    class LedBrightness(Enum):
        Dim = 0
        Bright = 1
        Off = 2

    @property
    @setting(name="LED Brightness", choices=SomeEnum, setter_name="set_led_brightness")
    def led_brightness(self) -> LedBrightness:
        """Return the LED brightness."""


Actions
"""""""

Use :meth:`@action <miio.devicestatus.action>` to create :class:`~miio.descriptors.ActionDescriptor`
objects for the device.
This will make all decorated actions accessible through :meth:`~miio.device.Device.actions` for downstream users.

.. code-block:: python

    @command()
    @action(name="Do Something", some_kwarg_for_downstream="hi there")
    def do_something(self):
        """Execute some action on the device."""

.. note::

    All keywords arguments not defined in the decorator signature will be available
    through the :attr:`~miio.descriptors.ActionDescriptor.extras` variable.

    This information can be used to pass information to the downstream users.


.. _adding_tests:

Adding tests
~~~~~~~~~~~~

.. TODO::
    Describe how to create tests.
    This part of documentation needs your help!
    Please consider submitting a pull request to update this.

.. _documentation:

Documentation
-------------

.. TODO::
    Describe how to write documentation.
    This part of documentation needs your help!
    Please consider submitting a pull request to update this.

.. _click: https://click.palletsprojects.com
.. _virtualenv: https://virtualenv.pypa.io
.. _isort: https://github.com/timothycrosley/isort
.. _pipenv: https://github.com/pypa/pipenv
.. _tox: https://tox.readthedocs.io
.. _pytest: https://docs.pytest.org
.. _black: https://github.com/psf/black
.. _pip: https://pypi.org/project/pip/
.. _precommit: https://pre-commit.com
.. _flake8: http://flake8.pycqa.org
.. _doc8: https://pypi.org/project/doc8/
