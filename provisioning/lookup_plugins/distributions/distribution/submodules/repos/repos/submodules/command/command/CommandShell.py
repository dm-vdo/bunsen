from __future__ import print_function

from .submodules.factory import FactoryShell

########################################################################
class CommandShell(FactoryShell):
  """Base class for command.
  """
  ####################################################################
  # Public methods
  ####################################################################
  def run(self):
    command = super(CommandShell, self).run()
    result = None
    try:
      result = command.run()
    except Exception as ex:
      if command.isDebug:
        raise ex
      print(ex)
    return result

  ####################################################################
  # Overridden methods
  ####################################################################

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################
