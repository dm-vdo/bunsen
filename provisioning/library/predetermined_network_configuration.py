#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import os
import subprocess

DOCUMENTATION = """
---
module: predetermined_network_configuration

short_description: Sets pre-determined values of pre-determined parameters

description:
  - "Sets pre-determined network parameter values inaccessible via ansible"

options:
  device:
    description:
      - Network device to configure
      - If not specified all devices will be discovered and configured
    required: False
    default: None
author:
  - Joe Shimkus (jshimkus@redhat.com)
"""

EXAMPLES = """
# Configure all network devices
- name: Configure all devices' parameters not available via ansible
  predetermined_network_configuration:

# Configure enP2p1s0v0 device
- name: Configure enP2p1s0v0 device's parameters not available via ansible
  predetermined_network_configuration:
    device: enP2p1s0v0
"""

RETURN = """
device:
    type: str
    description: The original device specified
message:
  type: str
  description: The output message generated
error:
  type: str
  description: Detailed error description
"""
#############################################################################
def getDevices(networkDevice = None):
  command = ["/usr/bin/nmcli", "--terse", "--fields",
             "DEVICE,STATE,CONNECTION", "device"]
  output = subprocess.check_output(command, stderr = subprocess.STDOUT)
  devices = {}
  for line in output.decode("utf-8").strip().split(os.linesep):
    (device, connected, connection) = line.split(":")
    devices[device] = {
                        "connected": connected == "connected",
                        "connection": connection
                      }
  if networkDevice is not None:
    try:
      devices = { networkDevice: devices[networkDevice] }
    except KeyError:
      devices = {}

  return devices

#############################################################################
def getConnectedDevices(networkDevice = None):
  return dict([(key, value)
                for (key, value) in getDevices(networkDevice).items()
                  if value["connected"]])

#############################################################################
def setDeviceIpParameters(networkDevice, attributes):
  command = ["/usr/bin/nmcli", "connection", "modify",
             attributes["connection"], "ipv4.may-fail", "no"]
  subprocess.check_output(command, stderr = subprocess.STDOUT)

#############################################################################
def runModule():
    # Define the available arguments/parameters that a user can pass to
  # the module.
  moduleArgs = {
    "device": { "type": "str", "required": False, "default": None}
  }

  # Seed the result dictionary.
  result = {
    "changed": False, "device": None, "message": "", "error" : None
  }

  # AnsibleModule will be the abstraction working with Ansible
  # including instantiation, common attributes and if we support
  # check mode.
  module = AnsibleModule(argument_spec = moduleArgs,
                         supports_check_mode = True)

  # Copy the device parameter to result.
  result["device"] = module.params["device"]

  # Only execute if not in check mode.
  if not module.check_mode:
    device = module.params["device"]
    try:
      connectedDevices = getConnectedDevices(device)
    except (OSError, CalledProcessError):
      module.fail_json(msg = "Failed getting connected devices", **result)

    if (device is not None) and (len(connectedDevices) == 0):
      result["message"] = "Network device {0} not found".format(device)
      module.fail_json(msg = "Network device not found", **result)

    for (key, value) in connectedDevices.items():
      try:
        setDeviceIpParameters(key, value)
        result["changed"] = True
      except (OSError, CalledProcessError):
        module.fail_json(msg = "Failed setting {0} ip parameters".format(key),
                         **result)

  # Success.
  result["message"] = "success"
  module.exit_json(**result)

def main():
  runModule()

if __name__ == '__main__':
  main()
