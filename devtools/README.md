# Devtools

This directory contains tooling useful for developers

## MiOT generator

This tool generates some boilerplate code for adding support for MIoT devices

1. If you know the model, use `python miottemplate.py download <model>` to download the description file.
  * This will download the model<->urn mapping file from http://miot-spec.org/miot-spec-v2/instances?status=all and store it locally
  * If you know the urn, you can use `--urn` to avoid downloading the mapping file (should not be necessary)

2. `python miottemplate.py print <description file>.json` prints out the siid/piid/aiid information from the spec file
