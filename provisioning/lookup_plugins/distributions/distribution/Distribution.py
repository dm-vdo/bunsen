import errno
import os
import re
import string
import subprocess
import yaml
from .submodules import (repos,
                         Defaults,
                         DefaultsFileFormatException,
                         Factory)

########################################################################
########################################################################
class DistributionException(Exception):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg, *args, **kwargs):
    super(DistributionException, self).__init__(*args, **kwargs)
    self._msg = msg

  ######################################################################
  def __str__(self):
    return self._msg

######################################################################
######################################################################
class DistributionNoDefaultException(DistributionException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg = "no distribution found for use as default",
               *args, **kwargs):
    super(DistributionNoDefaultException, self).__init__(msg, *args, **kwargs)

######################################################################
######################################################################
class DistributionUnknownCombinationException(DistributionException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg = "unknown combination", *args, **kwargs):
    super(DistributionUnknownCombinationException, self).__init__(msg,
                                                                  *args,
                                                                  **kwargs)

########################################################################
########################################################################
class Distribution(Factory):
  """Factory for instantiating objects which represent OS distributions.
  """
  ####################################################################
  # Factory-behavior attributes.
  ####################################################################
  __defaults = None

  # These dictionaries are indexed by architecture.  Each such accessed
  # item is a dictionary, indexed by distribution, which contains the
  # distributions available for the architecture.
  __mappingLatest = None
  __mappingNightly = None
  __mappingReleased = None

  ####################################################################
  # Instance-behavior attributes.
  ####################################################################
  _majorVersion = None
  _minorVersion = None
  _repoRoot = None
  _architecture = None

  ####################################################################
  # Public factory-behavior methods
  ####################################################################
  @classmethod
  def categoryMappingChoices(cls):
    """Returns a dictionary mapping the names of the distribution categories to
    the methods that return the available choices.
    """
    return { cls.defaultCategory()  : cls.choices,
             "latest"               : cls.choicesLatest,
             "nightly"              : cls.choicesNightly }

  ####################################################################
  @classmethod
  def categoryMappingMakeItem(cls):
    """Returns a dictionary mapping the names of the distribution categories to
    the methods to use in creating instances of same.
    """
    return { cls.defaultCategory()  : cls.makeItem,
             "latest"               : cls.makeItemLatest,
             "nightly"              : cls.makeItemNightly }

  ####################################################################
  @classmethod
  def choicesLatest(cls, architecture = None):
    return super(Distribution, cls).choices(("latest", architecture))

  ####################################################################
  @classmethod
  def choicesNightly(cls, architecture = None):
    return super(Distribution, cls).choices(("nightly", architecture))

  ####################################################################
  @classmethod
  def defaultCategory(cls):
    """Returns the name of the default category of distributions.
    """
    return "released"

  ####################################################################
  @classmethod
  def defaultDistribution(cls):
    # The distribution to use for machines which operate as servers but
    # are not under test.
    return cls.defaultChoice()

  ####################################################################
  @classmethod
  def makeItemLatest(cls, itemName, args = None, architecture = None):
    return cls._makeItemCommon(itemName, "latest", args, architecture)

  ####################################################################
  @classmethod
  def makeItemNightly(cls, itemName, args = None, architecture = None):
    return cls._makeItemCommon(itemName, "nightly", args, architecture)

  ####################################################################
  # Public instance-behavior methods
  ####################################################################
  @property
  def architecture(self):
    return self._architecture

  ####################################################################
  @property
  def beakerName(self):
    if self.__beakerName is None:
      beaker = None
      command = ["bkr", "distros-list", "--name", self.version]
      try:
        beaker = subprocess.Popen(command,
                                  stdin = subprocess.PIPE,
                                  stdout = subprocess.PIPE,
                                  stderr = subprocess.STDOUT)
      except OSError as ex:
        if ex.errno != errno.ENOENT:
          raise

      # If there's no beaker we default to the wildcard version and hope
      # for the best.
      if beaker is None:
        self.__beakerName = "{0}%".format(self.version)
      else:
        beaker.communicate()
        if beaker.returncode == 0:
          self.__beakerName = self.version
        else:
          # No base version; try the wildcard.
          command = ["bkr", "distros-list", "--name",
                      "{}%".format(self.version)]
          beaker = subprocess.Popen(command,
                                    stdin = subprocess.PIPE,
                                    stdout = subprocess.PIPE,
                                    stderr = subprocess.STDOUT)
          beaker.communicate()
          if beaker.returncode != 0:
            raise Exception("no beaker image for {0}".format(self.version))

          self.__beakerName = "{}%".format(self.version)

    return self.__beakerName

  ####################################################################
  @property
  def bootOptions(self):
    return ""

  ####################################################################
  @property
  def buildTag(self):
    return "{0}".format(self.version)

  ####################################################################
  @property
  def defaultUdsUri(self):
    return self._distroDefault(self._defaults().content([self.versionName,
                                                         "uds"]))

  ####################################################################
  @property
  def defaultVdoUri(self):
    return self._distroDefault(self._defaults().content([self.versionName,
                                                         "vdo"]))

  ####################################################################
  @property
  def family(self):
    return "{0}{1}".format(self._familyPrefix, self.majorVersion)

  ####################################################################
  @property
  def kickStart(self):
    return "harness='restraint-rhts beakerlib-redhat'"

  ####################################################################
  @property
  def mainRepo(self):
    return "{0}/{1}/$basearch/os".format(self.repoRoot, self.variant)

  ####################################################################
  @property
  def majorVersion(self):
    return self._majorVersion

  ####################################################################
  @property
  def minorVersion(self):
    return self._minorVersion

  ####################################################################
  @property
  def repoRoot(self):
    return self._repoRoot

  ####################################################################
  @property
  def specialRepos(self):
    return []

  ####################################################################
  @property
  def specialRepoRoots(self):
    return []

  ####################################################################
  @property
  def tags(self):
    return None

  ####################################################################
  @property
  def variant(self):
    raise NotImplementedError

  ####################################################################
  @property
  def version(self):
    version = "{0}-{1}".format(self.versionName.lower(),
                               self.majorVersion)
    if self.minorVersion is not None:
      version = "{0}.{1}".format(version, self.minorVersion)
    return version

  ####################################################################
  @property
  def versionName(self):
    return self._versionName()

  ####################################################################
  @property
  def versionNumber(self):
    number = "{0}".format(self.majorVersion)
    if self.minorVersion is not None:
      number = "{0}.{1}".format(number, self.minorVersion)
    return number

  ####################################################################
  @property
  def virtualBoxRepo(self):
    return "http://download.virtualbox.org" \
              "/virtualbox/rpm/{0}/$releasever/$basearch".format(
                                                            self.versionName)

  ####################################################################
  # Overridden factory-behavior methods
  ####################################################################
  @classmethod
  def choices(cls, architecture = None):
    return super(Distribution, cls).choices((cls.defaultCategory(),
                                             architecture))

  ####################################################################
  @classmethod
  def _defaultChoice(cls):
    from .distributions import Fedora

    defaultDistribution = cls._defaults().content(["distribution"])
    family = cls._defaults().content(["family"], defaultDistribution).lower()
    major = cls._defaults().content(["major"], defaultDistribution)
    minor = (None if family == "fedora"
                  else cls._defaults().content(["minor"], defaultDistribution))

    distributionName = "{0}{1}{2}".format(family,
                                          major,
                                          minor if minor is not None else "")

    distributions = dict([(x.name(), x) for x in cls.choices()])
    distribution = None
    try:
      distribution = distributions[distributionName]
    except KeyError:
      # The specified distribution was not available.
      # Use the most recent member of the specified family.
      familyClasses = dict([(float(x(None).versionNumber), x)
                            for x in cls.choices()
                              if x._versionName() == family])
      if len(familyClasses) > 0:
        distribution = familyClasses[max(familyClasses)]
      else:
        # Use the most recent available Fedora.
        fedoras = dict([(float(x(None).versionNumber), x)
                        for x in cls.choices() if issubclass(x, Fedora)])
        if len(fedoras) > 0:
          distribution = fedoras[max(fedoras)]

    if distribution is None:
      raise DistributionNoDefaultException()
    return distribution

  ####################################################################
  @classmethod
  def _mapping(cls, option = None):
    """'option', if present, is a tuple of (category, architecture) - both may
    be None - which indicates what mapping to utilize.

    A (category, architecture) of (None, None) is equivalent to not specifying
    an option, for which the default is to use the default category and
    architecture.
    """
    category = None
    architecture = None
    if option is not None:
      (category, architecture) = option
    if category is None:
      category = cls.defaultCategory()
    if architecture is None:
      architecture = repos.Architecture.defaultChoice().name()

    mapping = { cls.defaultCategory() : cls._mappingReleased,
                "latest"              : cls._mappingLatest,
                "nightly"             : cls._mappingNightly }

    return mapping[category](architecture)

  ####################################################################
  @classmethod
  def makeItem(cls, itemName, args = None, architecture = None):
    return cls._makeItemCommon(itemName, cls.defaultCategory(), args,
                               architecture)

  ####################################################################
  # Overridden instance-behavior methods
  ####################################################################
  def __init__(self, args):
    super(Distribution, self).__init__(args)
    self.__beakerName = None

  ####################################################################
  # Protected factory-behavior methods
  ####################################################################
  @classmethod
  def _allowableRoots(cls, roots):
    """Filters out those roots whose versions are less than that specified in
    the defaults.
    """
    (major, minor) = cls._minimumVersion()
    minimumVersion = float(major if minor is None
                                  else "{0}.{1}".format(major, minor))

    roots = dict([(key, value) for (key, value) in roots.items()
                                if float(key) >= minimumVersion])
    return roots

  ####################################################################
  @classmethod
  def _defaults(cls):
    if cls.__defaults is None:
      cls.__defaults = Defaults(os.path.join(
                                  os.path.dirname(
                                    os.path.realpath(__file__)),
                                  "..", "defaults.yml"))
    return cls.__defaults

  ####################################################################
  @classmethod
  def _latestRoots(cls, architecture):
    """Returns the available latest roots for the specified architecture
    filtered by the limits specified in the defaults file.
    """
    return cls._allowableRoots(
              cls._repoClass().availableLatestRoots(architecture))

  ####################################################################
  @classmethod
  def _makeDistributionMapping(cls, architecture, roots):
    mapping = {}

    for klass in roots:
      for (key, value) in roots[klass].items():
        splitKey = key.split(".", 1)
        major = int(splitKey[0])
        minor = None if len(splitKey) < 2 else int(splitKey[1])
        name = "{0}{1}{2}".format(klass.className().lower(),
                                  major,
                                  "" if minor is None else minor)
        mapping[name] = type("{0}{1}{2}".format(klass.className(),
                                                major,
                                                "" if minor is None
                                                   else minor),
                             (klass,),
                             dict(_available = True,
                                  _majorVersion = major,
                                  _minorVersion = minor,
                                  _name = name,
                                  _repoRoot = value,
                                  _architecture = architecture))
    return mapping

  ####################################################################
  @classmethod
  def _makeItemCommon(cls, itemName, category, args = None,
                      architecture = None):
    if architecture is None:
      architecture = repos.Architecture.defaultChoice().name()
    try:
      item = cls.item(itemName, (category, architecture))(args)
    except ValueError:
      raise DistributionUnknownCombinationException(
              "unknown {0} combination: {1}/{2}".format(cls.className(),
                                                        itemName,
                                                        architecture))
    return item

  ####################################################################
  @classmethod
  def _mappingLatest(cls, architecture):
    if cls.__mappingLatest is None:
      cls.__mappingLatest = {}

    if architecture not in cls.__mappingLatest:
      cls.__mappingLatest[architecture] = (
        cls._makeDistributionMapping(
                                architecture,
                                dict([(klass,
                                       klass._latestRoots(architecture))
                                      for klass in
                                        super(Distribution,
                                              cls)._mapping().values()])))
    return cls.__mappingLatest[architecture]

  ####################################################################
  @classmethod
  def _mappingNightly(cls, architecture):
    if cls.__mappingNightly is None:
      cls.__mappingNightly = {}

    if architecture not in cls.__mappingNightly:
      cls.__mappingNightly[architecture] = (
        cls._makeDistributionMapping(
                                architecture,
                                dict([(klass,
                                       klass._nightlyRoots(architecture))
                                      for klass in
                                        super(Distribution,
                                              cls)._mapping().values()])))
    return cls.__mappingNightly[architecture]

  ####################################################################
  @classmethod
  def _mappingReleased(cls, architecture):
    if cls.__mappingReleased is None:
      cls.__mappingReleased = {}

    if architecture not in cls.__mappingReleased:
      cls.__mappingReleased[architecture] = (
        cls._makeDistributionMapping(
                                architecture,
                                dict([(klass,
                                       klass._releasedRoots(architecture))
                                      for klass in
                                        super(Distribution,
                                              cls)._mapping().values()])))
    return cls.__mappingReleased[architecture]

  ####################################################################
  @classmethod
  def _minimumVersion(cls):
    return (cls._defaults().content([cls._versionName(), "minimum", "major"]),
            None)

  ####################################################################
  @classmethod
  def _nightlyRoots(cls, architecture):
    """Returns the available nightly roots for the specified architecture
    filtered by the limits specified in the defaults file.
    """
    return cls._allowableRoots(
            cls._repoClass().availableNightlyRoots(architecture))

  ####################################################################
  @classmethod
  def _releasedRoots(cls, architecture):
    """Returns the available released roots for the specified architecture
    filtered by the limits specified in the defaults file.
    """
    return cls._allowableRoots(cls._repoClass().availableRoots(architecture))

  ####################################################################
  @classmethod
  def _repoClass(cls):
    """Returns the repo class associated with the distribution."""
    raise NotImplementedError

  ####################################################################
  @classmethod
  def _versionName(cls):
    return cls.className().lower().rstrip(string.digits)

  ####################################################################
  # Protected instance-behavior methods
  ####################################################################
  def _distroDefault(self, sourceDictionary):
    """The input dictionary is dual-level structured akin to

      default: //eng/uds-releases/krusty
      fedora2\d$:
        default: //eng/uds-releases/krusty
        fedora28: //eng/uds-releases/jasper
        fedora29: //eng/uds-releases/krusty
      fedora3\d$:
        default: //eng/uds-releases/krusty

    where the first-level keys are regexes to match all distributions with a
    specific prefix.
    """
    regexMatches = list(filter(lambda x: re.match(x, self.name()) is not None,
                               sourceDictionary.keys()))
    if len(regexMatches) > 1:
      raise DefaultsFileFormatException("multiple regex matches found")

    default = None
    if len(regexMatches) == 0:
      default = self._defaults().content(["default"], sourceDictionary)
    else:
      distroMatches = list(
                        filter(lambda x: re.match(x, self.name()) is not None,
                               sourceDictionary[regexMatches[0]].keys()))
      if len(distroMatches) > 1:
        raise DefaultsFileFormatException(
                                        "multiple distribution matches found")
      if len(distroMatches) == 0:
        default = self._defaults().content(["default"],
                                           sourceDictionary[regexMatches[0]])
      else:
        default = sourceDictionary[regexMatches[0]][distroMatches[0]]

    return default

  ####################################################################
  @property
  def _familyPrefix(self):
    raise NotImplementedError

  ####################################################################
  # Private factory-behavior methods
  ####################################################################

  ####################################################################
  # Private instance-behavior methods
  ####################################################################
