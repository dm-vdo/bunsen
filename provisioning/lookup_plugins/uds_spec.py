DOCUMENTATION = """
  lookup: uds_spec
  author: Joe Shimkus <jshimkus@redhat.com>
  version_added: "0.1"
  short_description: return uds specs using default uds urls for distributions
  description:
    - This lookup returns the uds specs using default uds urls for specified
      distributions.
  arguments:
    - terms:  a list of strings specifying distributions;
              e.g.; rhel82, redhat82 or fedora31
  notes:
    - If the variable 'permabuild_uds_directory' is defined it will be
      prepended to the 'dest' field in the returned spec.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from spec import UdsSpec

class LookupModule(UdsSpec):
  pass
