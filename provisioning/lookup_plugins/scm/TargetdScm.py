from __future__ import print_function

from .Scm import Scm

########################################################################
class TargetdScm(Scm):
  """Targetd Source Control Management class.
  """

  ####################################################################
  # Public methods
  ####################################################################

  ####################################################################
  # Overridden methods
  ####################################################################
  @property
  def source(self):
    """Returns the source code to which this scm applies; e.g., uds.
    """
    return "targetd"

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################
