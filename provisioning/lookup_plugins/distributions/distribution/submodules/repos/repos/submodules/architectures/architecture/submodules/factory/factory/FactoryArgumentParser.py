import argparse
import os
import platform

########################################################################
class FactoryArgumentParser(argparse.ArgumentParser):
  """Argument parser for factory items.
  """

  ####################################################################
  # Public methods
  ####################################################################
  @classmethod
  def parserDestination(cls):
    return "selection"

  ####################################################################
  @classmethod
  def parserHelp(cls):
    return "description"

  ####################################################################
  @classmethod
  def parserMetaVar(cls):
    return cls.parserDestination()

  ####################################################################
  @classmethod
  def parserTitle(cls):
    return "factory item specification"

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, factoryClass):
    super(FactoryArgumentParser, self).__init__()

    (major, minor, patch) = map(lambda x: int(x),
                                platform.python_version_tuple())
    if (major < 3) or ((major == 3) and (minor < 7)):
      parserAdder = self.add_subparsers(
                                title = self.parserTitle(),
                                help = self.parserHelp(),
                                dest = self.parserDestination(),
                                metavar = self.parserMetaVar(),
                                parser_class = argparse.ArgumentParser)
    else:
      parserAdder = self.add_subparsers(
                                title = self.parserTitle(),
                                help = self.parserHelp(),
                                dest = self.parserDestination(),
                                metavar = self.parserMetaVar(),
                                parser_class = argparse.ArgumentParser,
                                required = True)

    # Add a subparser for each command.
    for item in factoryClass.choices():
      parents = item.parserParents()
      epilog = os.linesep.join([parser.epilog for parser in parents
                                              if parser.epilog is not None])
      parserAdder.add_parser(item.name(),
                             formatter_class
                              = argparse.RawDescriptionHelpFormatter,
                             parents = parents,
                             help = item.help(),
                             epilog = epilog)

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################
