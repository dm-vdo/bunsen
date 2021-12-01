import argparse
from .submodules.factory import Factory
from .CommandArgumentParser import (CommandArgumentParser,
                                    CommandNullArgumentParser)

########################################################################
class Command(Factory):
  ####################################################################
  # Public factory-behavior methods
  ####################################################################

  ####################################################################
  # Public instance-behavior methods
  ####################################################################
  @property
  def isDebug(self):
    # Is debugging enabled?
    return self.args.commandDebug

  ####################################################################
  @property
  def isVerbose(self):
    # Is verbose enabled?
    return self.verbosity > 0

  ####################################################################
  @property
  def verbosity(self):
    # Is verbose enabled?
    return self.args.commandVerbosity

  ####################################################################
  def run(self):
    # Execute the command.
    raise NotImplementedError("COMMAND NOT IMPLEMENTED")

  ####################################################################
  # Overridden factory-behavior methods
  ####################################################################
  @classmethod
  def _argumentParserClass(cls):
    return CommandArgumentParser

  ####################################################################
  @classmethod
  def makeItem(cls, itemName = None, args = None):
    item = None

    if (itemName is not None) or (len(cls.choices()) > 0):
      item = super(Command, cls).makeItem(itemName, args)
    else:
      if args is None:
        parser = cls._nullArgumentParser()
        args = parser.parse_args()
      item = cls._rootClass()(args)

    return item

  ####################################################################
  # Overridden instance-behavior methods
  ####################################################################
  @classmethod
  def help(cls):
    return "execute command {0}".format(cls.name())

  ####################################################################
  @classmethod
  def parserParents(cls):
    parser = argparse.ArgumentParser(add_help = False)

    parser.add_argument("--debug",
                        help = "turn on debugging mode",
                        dest = "commandDebug",
                        action = "store_true")
    parser.add_argument("--verbose", "-v",
                        help = "turn on/increase verbose mode",
                        dest = "commandVerbosity",
                        action = "count",
                        default = 0)

    parents = super(Command, cls).parserParents()
    parents.append(parser)
    return parents

  ####################################################################
  # Protected factory-behavior methods
  ####################################################################
  @classmethod
  def _nullArgumentParser(cls):
    return cls._nullArgumentParserClass()(cls._rootClass())

  ####################################################################
  @classmethod
  def _nullArgumentParserClass(cls):
    return CommandNullArgumentParser

  ####################################################################
  # Protected instance-behavior methods
  ####################################################################

  ####################################################################
  # Private factory-behavior methods
  ####################################################################

  ####################################################################
  # Private instance-behavior methods
  ####################################################################
