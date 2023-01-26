.. python-miio documentation master file, created by
   sphinx-quickstart on Wed Oct 18 03:50:00 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. include:: ../README.md
   :parser: myst_parser.sphinx_


History
-------
This project was started to allow controlling locally available Xiaomi
Vacuum cleaner robot with Python (hence the old name ``python-mirobo``),
however, thanks to contributors it has been extended to allow
controlling other Xiaomi devices using the same protocol `miIO protocol <https://github.com/OpenMiHome/mihome-binary-protocol>`__.
(`another source for vacuum-specific
documentation <https://github.com/marcelrv/XiaomiRobotVacuumProtocol>`__)

First and foremost thanks for the nice people over `ioBroker
forum <http://forum.iobroker.net/viewtopic.php?f=23&t=4898>`__ who
figured out the encryption to make this library possible.
Furthermore thanks goes to contributors of this project
who have helped to extend this to cover not only the vacuum cleaner.

.. toctree::
    :maxdepth: 1
    :caption: Contents:

    Home <self>
    discovery
    troubleshooting
    contributing
    simulator
    device_docs/index
    push_server

    API <api/miio>
