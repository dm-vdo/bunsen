from scm import RtslibScm
from .internal import Spec

class RtslibSpec(Spec):
  ####################################################################
  # Overridden methods
  ####################################################################
  @property
  def _destPrefixVariable(self):
    return "permabuild_rtslib_directory"

  ####################################################################
  @property
  def _scmClass(self):
    return RtslibScm

  ####################################################################
  @property
  def _urlPrefix(self):
    return "https://gitlab.cee.redhat.com/"

  ####################################################################
  def _distributionRequest(self, distribution):
    return "jshimkus-bits/bunsen/third-party/rtslib-fb.git"
