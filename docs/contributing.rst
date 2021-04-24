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

Adding support for new devices
------------------------------

.. _checklist:

Development checklist
~~~~~~~~~~~~~~~~~~~~~

1. All device classes are derived from either :class:`miio.device.Device` (for MiIO)
   or :class:`miio.miot_device.MiotDevice` (for MiOT) (:ref:`Minimal example`).
2. All commands and their arguments should be decorated with `@command` decorator,
   which will make them accessible to `miiocli` (:ref:`miiocli`).
3. Status containers is derived from `DeviceStatus` class and all properties should
   have type annotations for their return values.
4. Creating tests (:ref:`adding_tests`).
5. Updating documentation is generally not needed as the API documentation
   will be generated automatically.


Minimal example
~~~~~~~~~~~~~~~

.. TODO::
    Add or link to an example.


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


Status containers
~~~~~~~~~~~~~~~~~

The status container (returned by `status()` method of the device class)
is the main way for library users to access properties exposed by the device.
The status container should inherit :class:`miio.device.DeviceStatus` to ensure a generic :meth:`__repr__`.



MiIO devices
~~~~~~~~~~~~

.. TODO::
    Add instructions how to extract protocol from network captures


MiOT devices
~~~~~~~~~~~~

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
