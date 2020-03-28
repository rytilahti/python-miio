# Devtools

This directory contains tooling useful for developers

## MiOT generator

This tool generates some boilerplate code for adding support for MIoT devices

1. Obtain device type from http://miot-spec.org/miot-spec-v2/instances?status=all
2. Execute `python miottemplate.py download <type>` to download the description file.
3. Execute `python miottemplate.py generate <file>` to generate pseudo-python for the device.
