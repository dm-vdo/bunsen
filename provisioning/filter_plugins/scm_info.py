# Custom jinja2 filters scm_request(X) and scm_type(X).

# Argument X is a URI specifying an SCM request.

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                + os.path.sep + "lookup_plugins")
from scm import Scm

# Output is the URI's path together with any parameters and fragments.
def scm_request(uri):
  return Scm(uri).request

# Output is the name of the SCM, which may differ from the scheme contained
# in the URI.  If the scheme-to-scm mapping does not contain an entry
# for the scheme the result will be "git".
def scm_type(uri):
  return Scm(uri).type

# Incorporate the filters in the execution space.
class FilterModule(object):
    def filters(self):
        return {
            'scm_request' : scm_request,
            'scm_type'    : scm_type,
        }
