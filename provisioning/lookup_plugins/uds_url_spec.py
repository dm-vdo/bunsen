DOCUMENTATION = """
  lookup: uds_url_spec
  author: Joe Shimkus <jshimkus@redhat.com>
  version_added: "0.1"
  short_description: return uds specs based on urls
  description:
    - This lookup returns the uds specs using the specified urls
  arguments:
    - terms:  a list of strings specifying uds urls
  notes:
    None
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from spec import UdsUrlSpec

class LookupModule(UdsUrlSpec):
  pass
