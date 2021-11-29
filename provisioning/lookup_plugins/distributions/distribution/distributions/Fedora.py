from ..Distribution import Distribution
from ..submodules import repos

########################################################################
class Fedora(Distribution):
  """Class for Fedora distributions.
  """
  # Available for use.
  _available = True

  ####################################################################
  # Public methods
  ####################################################################

  ####################################################################
  # Overridden methods
  ####################################################################
  @property
  def bootOptions(self):
    options = super(Fedora, self).bootOptions
    if self.majorVersion == 32:
      options += (" " + "inst.updates="
        + "http://vdo-image-store.permabit.lab.eng.bos.redhat.com"
        + "/repository/beaker/rhbz1830515.img")
    return options.strip()

  ####################################################################
  @property
  def variant(self):
    return "Everything"

  ####################################################################
  @classmethod
  def _repoClass(cls):
    return repos.Fedora

  ####################################################################
  @property
  def _familyPrefix(self):
    return "Fedora"

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################
