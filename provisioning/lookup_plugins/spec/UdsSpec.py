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
    return "p4://pbitperforce01.permabit.lab.eng.bos.redhat.com:1666/"

  ####################################################################
  def _distributionRequest(self, distribution):
    return distribution.defaultUdsUri.replace("//", "", 1)

  ####################################################################
  def _makeSpec(self, scm):
    spec = super(UdsSpec, self)._makeSpec(scm)
    spec["bare"] = "yes"
    return spec

######################################################################
######################################################################
class UdsUrlSpec(UdsSpec, UrlSpec):
  pass
