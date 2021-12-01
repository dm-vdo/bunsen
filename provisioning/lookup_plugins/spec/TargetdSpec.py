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
    return "https://gitlab.cee.redhat.com/"

  ####################################################################
  def _distributionRequest(self, distribution):
    return "vdo/open-sourcing/tools/third/targetd.git"
