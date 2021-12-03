from scm import UdsScm
from .internal import Spec, UrlSpec

######################################################################
######################################################################
class UdsSpec(Spec):
  ####################################################################
  # Overridden methods
  ####################################################################
  @property
  def _destPrefixVariable(self):
    return "permabuild_uds_directory"

  ####################################################################
  @property
  def _scmClass(self):
    return UdsScm

  ####################################################################
  @property
  def _urlPrefix(self):
    external = self._variables["externals"]["first-party"]["uds-uri"]
    return "{0}{1}".format(external["host"]["schema"],
                           external["host"]["name"])

  ####################################################################
  def _distributionRequest(self, distribution):
    return distribution.defaultUdsUri.replace("//", "/", 1)

  ####################################################################
  def _makeSpec(self, scm):
    spec = super(UdsSpec, self)._makeSpec(scm)
    spec["bare"] = "yes"
    return spec

######################################################################
######################################################################
class UdsUrlSpec(UdsSpec, UrlSpec):
  pass
