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
    external = self._variables["externals"]["third-party"]["rtslib"]
    return "{0}{1}".format(external["host"]["schema"],
                           external["host"]["name"])

  ####################################################################
  def _distributionRequest(self, distribution):
    external = self._variables["externals"]["third-party"]["rtslib"]
    return external["host"]["path"]
