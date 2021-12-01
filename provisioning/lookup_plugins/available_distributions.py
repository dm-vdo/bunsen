DOCUMENTATION = """
  lookup: available_distributions
  author: Joe Shimkus <jshimkus@redhat.com>
  version_added: "0.1"
  short_description: return names of known distributions for bunsen
  description:
    - This lookup returns the names of the known distributions for bunsen.
  arguments:
    - none
  notes:
    - none
"""
import os
import platform
import sys

(major, minor, _) = map(lambda x: int(x), platform.python_version_tuple())
sys.path.append("/usr/local/lib/python{0}.{1}/site-packages".format(major,
                                                                    minor))

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from distributions import Distribution

class LookupModule(LookupBase):
  def run(self, _terms = None, variables = None, **kwargs):
      if (_terms is not None) and (len(_terms) > 0):
        raise AnsibleError("incorrect number of arguments")

      return [distribution.name().upper()
              for distribution in Distribution.choices()]
