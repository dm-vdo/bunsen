from ..Distribution import (Distribution,
                            DistributionUnknownCombinationException)
from ..submodules import repos

########################################################################
class CentOS(Distribution):
  """Class for CentOS distributions.
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
  def beakerName(self):
    return self._filteredBeakerName(super(CentOS, self).beakerName)

  ####################################################################
  @property
  def specialRepoRoots(self):
    roots = super(CentOS, self).specialRepoRoots
    try:
      roots.append(self.makeItem(
                    self._distroDefault(
                      self._defaults().content([self.versionName,
                                                "specialRepos"])),
                    architecture = self.architecture).repoRoot)
    except DistributionUnknownCombinationException:
      # The defaults specifies a distribution that isn't available.
      pass
    return roots

  ####################################################################
  @property
  def variant(self):
    return "Server" if self.majorVersion < 8 else "BaseOS"

  ####################################################################
  @classmethod
  def _minimumVersion(cls):
    (major, _) = super(CentOS, cls)._minimumVersion()
    return (major,
            cls._defaults().content([cls._versionName(), "minimum", "minor"]))

  ####################################################################
  @classmethod
  def _repoClass(cls):
    return repos.CentOS

  ####################################################################
  @property
  def _familyPrefix(self):
    return "CentOSLinux"

  ####################################################################
  # Protected methods
  ####################################################################
  def _filteredBeakerName(self, name):
    # If the name ends with the wildcard character '%' it indicates we
    # did not get an answer from Beaker directly.
    # Because Beaker (at present?) is not following the same naming
    # convention for CentOS as it does for RHEL (including both major and
    # minor numbers) we rejigger the name to just include the major.
    if name.endswith("%"):
      name = "{0}-{1}%".format(self.versionName.lower(), self.majorVersion)
    return name


  ####################################################################
  # Private methods
  ####################################################################
