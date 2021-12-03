from scm import TargetdScm
from .internal import Spec

class TargetdSpec(Spec):
  ####################################################################
  # Overridden methods
  ####################################################################
  @property
  def _destPrefixVariable(self):
    return "permabuild_targetd_directory"

  ####################################################################
  @property
  def _scmClass(self):
    return TargetdScm

  ####################################################################
  @property
  def _urlPrefix(self):
    external = self._variables["externals"]["third-party"]["targetd"]
    return "{0}{1}".format(external["host"]["schema"],
                           external["host"]["name"])

  ####################################################################
  def _distributionRequest(self, distribution):
    external = self._variables["externals"]["third-party"]["targetd"]
    return external["host"]["path"]
