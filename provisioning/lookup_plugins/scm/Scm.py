from __future__ import print_function

import os
import platform
if int(platform.python_version_tuple()[0]) < 3:
  import urlparse
else:
  from urllib import parse as urlparse

########################################################################
class Scm(object):
  """Source Control Management class.
  """

  ####################################################################
  # Public methods
  ####################################################################
  @property
  def dest(self):
    return "{0}{1}.{2}.{3}".format(self.__destPrefix,
                                   self.source,
                                   "common" if self.distribution is None
                                            else self.distribution,
                                   self.type)

  ####################################################################
  @property
  def distribution(self):
    return self.__distribution

  ####################################################################
  @property
  def netloc(self):
    return urlparse.urlparse(self.url).netloc

  ####################################################################
  @property
  def scheme(self):
    return urlparse.urlparse(self.url).scheme

  ####################################################################
  @property
  def source(self):
    """Returns the source code to which this spec applies; e.g., uds.
    """
    raise NotImplementedError

  ####################################################################
  @property
  def url(self):
    return self.__url

  ####################################################################
  @property
  def request(self):
    """Returns the url's path together with any parameters and fragments.
    """
    return self.url.split("{0}://{1}".format(self.scheme, self.netloc), 1)[1]

  ####################################################################
  @property
  def type(self):
    """Returns the name of the SCM, which may differ from the scheme contained
    in the url.

    If the scheme-to-scm mapping does not contain an entry for the scheme the
    result will be "git".
    """
    git = "git"
    schemeToScm = { "git"   : git,
                    "http"  : git }
    try:
      return schemeToScm[self.scheme]
    except KeyError:
      return git

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, url, destPrefix = None, distribution = None):
    super(Scm, self).__init__()
    self.__url = url
    self.__destPrefix = "" if destPrefix is None else (destPrefix
                                                        + os.path.sep)
    self.__distribution = distribution

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################
