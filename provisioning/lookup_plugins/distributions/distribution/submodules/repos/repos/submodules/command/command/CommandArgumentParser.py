import argparse
import os
from .submodules.factory import FactoryArgumentParser

########################################################################
class CommandArgumentParser(FactoryArgumentParser):
  """Argument parser for commands.
  """

  ####################################################################
  # Public methods
  ####################################################################

  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def parserDestination(cls):
    return "command"

  ####################################################################
  @classmethod
  def parserTitle(cls):
    return "command specification"

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################

########################################################################
class CommandNullArgumentParser(argparse.ArgumentParser):
  """Argument parser for command line utilities which don't have subcommands.
  """
  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, factoryItemClass):
    parents = factoryItemClass.parserParents()
    description = os.linesep.join([parser.description for parser in parents
                                            if parser.description is not None])
    epilog = os.linesep.join([parser.epilog for parser in parents
                                            if parser.epilog is not None])
    super(CommandNullArgumentParser, self).__init__(
                      formatter_class = argparse.RawDescriptionHelpFormatter,
                      description = description,
                      epilog = epilog,
                      parents = parents)
