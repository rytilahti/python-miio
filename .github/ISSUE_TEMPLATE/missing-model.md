---
name: Missing model information for a supported device
about: Inform about functioning device that prints out a warning about unsupported model
title: ''
labels: missing model
assignees: ''

---

If you are receiving a warning indicating an unsupported model (`Found an unsupported model '<model>' for class '<class>'.`),
this means that the implementation does not list your model as supported.

If it is working fine for you nevertheless, feel free to open an issue or create a PR to add the model to the `_supported_models` ([example](https://github.com/rytilahti/python-miio/blob/72cd423433ad71918b5a8e55833a5b2eda9877a5/miio/integrations/vacuum/roborock/vacuum.py#L125-L153)) for that class.

Before submitting, use the search to see if there is an existing issue for the device model, thanks!

**Device information:**

  - Name(s) of the device:
  - Link:

Use `miiocli device --ip <ip address> --token <token>`.

  - Model: [e.g., lumi.gateway.v3]
  - Hardware version:
  - Firmware version:
