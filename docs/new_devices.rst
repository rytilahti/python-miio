Contributing
************

Contributions of any sort are more than welcome,
so we hope this short introduction will help you to get started!
Shortly put: we use black_ to format our code, isort_ to sort our imports, pytest_ to test our code,
flake8_ to do its checks, and doc8_ for documentation checks.

Development environment
-----------------------

This section will shortly go through how to get you started with a working development environment.
We use `poetry <https://python-poetry.org/>`__ for managing the dependencies and packaging, so simply execute:

    poetry install

To verify the installation, simply launch tox_ to run all the checks::

    tox

In order to make feedback loops faster, we automate our code checks by using precommit_ hooks.
Therefore the first step after setting up the development environment is to install them::

    pre-commit install

You can always `execute the checks <#code-checks>`_ also without doing a commit.

Code checks
~~~~~~~~~~~

Instead of running all available checks during development,
it is also possible to execute only the code checks by calling.
This will execute the same checks that would be done automatically by precommit_ when you make a commit::

    tox -e lint

Tests
~~~~~

We prefer to have tests for our code, so we use pytest_ you can also use by executing::

    pytest miio

When adding support for a new device or extending an already existing one,
please do not forget to create tests for your code.

Generating documentation
~~~~~~~~~~~~~~~~~~~~~~~~

You can compile the documentation and open it locally in your browser::

    sphinx docs/ generated_docs
    $BROWSER generated_docs/index.html

Replace `$BROWSER` with your preferred browser, if the environment variable is not set.

Adding support for new devices
------------------------------

The `miio javascript library <https://github.com/aholstenson/miio>`__
contains some hints on devices which could be supported, however, the
Xiaomi Smart Home gateway (`Home Assistant
component <https://github.com/lazcad/homeassistant>`__ already work in
progress) as well as Yeelight bulbs are currently not in the scope of
this project.

.. TODO::
    Add instructions how to extract protocol from network captures

Adding tests
------------

.. TODO::
    Describe how to create tests.
    This part of documentation needs your help!
    Please consider submitting a pull request to update this.

Documentation
-------------

.. TODO::
    Describe how to write documentation.
    This part of documentation needs your help!
    Please consider submitting a pull request to update this.

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
