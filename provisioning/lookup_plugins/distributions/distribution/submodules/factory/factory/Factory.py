from .FactoryArgumentParser import FactoryArgumentParser

########################################################################
class Factory(object):
  """Factory for instantiating objects.
  """
  ####################################################################
  # Factory-behavior attributes.
  ####################################################################
  __mapping = None

  ####################################################################
  # Instance-behavior attributes.
  ####################################################################
  # If _available is not overridden as True the class will not be identified as
  # an available item.
  _available = False

  # Use _name to give each item a name different from their class name (in
  # lowercase).  Must be a unique, contiguous set of characters suitable for
  # use as an argparse choice value.
  _name = None

  ####################################################################
  # Public factory-behavior methods
  ####################################################################
  @classmethod
  def choices(cls, option = None):
    """'option' is a subclass-dependent parameter specifying what targets
    should be mapped.  This allows runtime usage of alternate mappings.

    A value of None indicates that the subclass's default mapping is to be
    used.
    """
    return sorted(cls._mapping(option).values(),
                  key = lambda klass: klass.name())

  ####################################################################
  @classmethod
  def defaultChoice(cls):
    choice = cls._defaultChoice()
    if (choice is not None) and (not choice.available()):
      choice = None
    return choice

  ####################################################################
  @classmethod
  def item(cls, name, option = None):
    """'option' is a subclass-dependent parameter specifying what targets
    should be mapped.  This allows runtime usage of alternate mappings.

    A value of None indicates that the subclass's default mapping is to be
    used.
    """
    try:
      item = cls._mapping(option)[name]
    except KeyError:
      raise ValueError("unknown {0} item specified: {1}".format(
                        cls.className(), name))
    return item

  ####################################################################
  @classmethod
  def makeItem(cls, itemName = None, args = None):
    """Makes an item from the default mapping.
    """
    if itemName is None:
      parser = cls._argumentParser()
      if args is None:
        args = parser.parse_args()
      itemName = vars(args)[parser.parserDestination()]
    return cls.item(itemName)(args)

  ####################################################################
  # Public instance-behavior methods
  ####################################################################
  @classmethod
  def available(cls):
    return cls._available

  ####################################################################
  @classmethod
  def className(cls):
    return cls.__name__

  ####################################################################
  @classmethod
  def name(cls):
    return cls._name if cls._name is not None else cls.className().lower()

  ####################################################################
  @classmethod
  def help(cls):
    return "no special considerations"

  ####################################################################
  @classmethod
  def parserParents(cls):
    return []

  ####################################################################
  @property
  def args(self):
    return self.__args

  ####################################################################
  # Overridden factory-behavior methods
  ####################################################################

  ####################################################################
  # Overridden instance-behavior methods
  ####################################################################
  def __init__(self, args):
    super(Factory, self).__init__()
    self.__args = args

  ####################################################################
  # Protected factory-behavior methods
  ####################################################################
  @classmethod
  def _argumentParser(cls):
    return cls._argumentParserClass()(cls)

  ####################################################################
  @classmethod
  def _argumentParserClass(cls):
    return FactoryArgumentParser

  ####################################################################
  @classmethod
  def _defaultChoice(cls):
    return None

  ####################################################################
  @classmethod
  def _mapping(cls, option = None):
    """'option' is a subclass-dependent parameter specifying what targets
    should be mapped.  A value of None indicates that if a mapping already
    exists it can simply be reused.  If a mapping does not exist None indicates
    to create the subclass's default mapping and use that.
    """
    if cls.__mapping is None:
      # Available entities are identified by having a True availability.
      klasses = cls.__getClasses(cls._rootClass())
      cls.__mapping = dict([(klass.name(), klass) for klass in klasses])
    return cls.__mapping

  ####################################################################
  @classmethod
  def _rootClass(cls):
    return cls

  ####################################################################
  # Protected factory-behavior methods
  ####################################################################

  ####################################################################
  # Private factory-behavior methods
  ####################################################################
  @classmethod
  def __getClasses(cls, klass):
    klasses = [] if not klass.available() else [klass]
    for subclass in klass.__subclasses__():
      klasses.extend(cls.__getClasses(subclass))
    return klasses

  ####################################################################
  # Private instance-behavior methods
  ####################################################################
