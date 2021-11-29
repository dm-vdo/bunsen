import errno
import yaml

######################################################################
######################################################################
class DefaultsException(Exception):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg, *args, **kwargs):
    super(DefaultsException, self).__init__(*args, **kwargs)
    self._msg = msg

  ######################################################################
  def __str__(self):
    return self._msg

######################################################################
######################################################################
class DefaultsFileException(DefaultsException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg = "error with defaults file", *args, **kwargs):
    super(DefaultsFileException, self).__init__(msg, *args, **kwargs)

######################################################################
######################################################################
class DefaultsFileContentMissingException(DefaultsFileException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, missingContent, *args, **kwargs):
    super(DefaultsFileContentMissingException, self).__init__(
      "'{0}' missing".format(missingContent), *args, **kwargs)

######################################################################
######################################################################
class DefaultsFileDoesNotExistException(DefaultsFileException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg = "defaults file does not exist", *args, **kwargs):
    super(DefaultsFileDoesNotExistException, self).__init__(msg,
                                                            *args,
                                                            **kwargs)

######################################################################
######################################################################
class DefaultsFileFormatException(DefaultsFileException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg = "defaults file format invalid", *args, **kwargs):
    super(DefaultsFileFormatException, self).__init__(msg, *args, **kwargs)

######################################################################
######################################################################
class Defaults(object):
  ####################################################################
  # Public methods
  ####################################################################
  @property
  def filePath(self):
    return self.__filePath

  ####################################################################
  def content(self, path, sourceDictionary = None):
    """Returns the specified content from the defaults file or the specified
    dictionary.

    The path argument is a list specifying the key path to the value of
    interest.  In the case of the defaults file (i.e., no specified dictionary)
    this excludes the highest level key of 'defaults'.

    The source dictionary argument is provided for specifying a dictionary
    extracted from the defaults (one of local processing interest) while
    operating on said dictionary with the same overall defaults content checks.
    Note that the path is local to the specified dictionary thus any exception
    generated which includes the path will also be local to the specified
    dictionary.

    Both the defaults file and any specified source dictionary are treated as a
    dictionary of dictionaries of arbitrary depth.
    """
    return self._content(sourceDictionary if sourceDictionary is not None
                                          else self._defaults,
                         path)

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, filePath):
    super(Defaults, self).__init__()
    self.__filePath = filePath
    self.__defaults = self._loadDefaults()

  ####################################################################
  # Protected methods
  ####################################################################
  def _content(self, sourceDictionary, path):
    """Returns the specified content from the source dictionary.
    The source dictionary is a dictionary of dictionaries of arbitrary depth.
    The path argument is a list specifying the keyword path to the value
    of interest.
    """
    result = sourceDictionary
    missing = None
    for element in path:
      missing = element if missing is None else "/".join([missing, element])
      try:
        result = result[element]
      except KeyError:
        raise DefaultsFileContentMissingException(missing)
    return result

  ####################################################################
  @property
  def _defaults(self):
    return self.__defaults

  ####################################################################
  def _loadDefaults(self):
    defaults = None
    try:
      with open(self.filePath) as f:
        defaults = yaml.safe_load(f)
        if not isinstance(defaults, dict):
          raise DefaultsFileFormatException()
        try:
          defaults = self._content(defaults, ["defaults"])
        except DefaultsFileContentMissingException:
          raise DefaultsFileFormatException()
    except IOError as ex:
      if ex.errno != errno.ENOENT:
        raise
      raise DefaultsFileDoesNotExistException()

    return defaults

  ####################################################################
  # Private methods
  ####################################################################
