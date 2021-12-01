import os
import platform
import sys

(major, minor, _) = map(lambda x: int(x), platform.python_version_tuple())
sys.path.append("/usr/local/lib/python{0}.{1}/site-packages".format(major,
                                                                    minor))
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from distributions import Distribution
from scm import Scm

class Spec(LookupBase):
  ####################################################################
  # Overridden methods
  ####################################################################
  def run(self, terms, variables = None, **kwargs):
    if len(terms) == 0:
      raise AnsibleError("incorrect number of arguments")

    return self._run(terms, variables, **kwargs)

  ####################################################################
  # Protected methods
  ####################################################################
  @property
  def _destPrefixVariable(self):
    return None

  ####################################################################
  @property
  def _scmClass(self):
    raise NotImplementedError

  ####################################################################
  @property
  def _urlPrefix(self):
    return ""

  ####################################################################
  def _destPrefix(self, variables = None):
    prefix = None
    if (variables is not None) and (self._destPrefixVariable is not None):
      try:
        prefix = self._templar.template(variables[self._destPrefixVariable])
      except KeyError:
        pass
    return prefix

  ####################################################################
  def _distributionRequest(self, distribution):
    raise NotImplementedError

  ####################################################################
  def _makeScm(self, url, variables = None, distribution = None):
    return self._scmClass(url,
                          self._destPrefix(variables),
                          None if distribution is None
                                else distribution.name())

  ####################################################################
  def _makeSpec(self, scm):
    return { "url"      : scm.url,
             "src"      : scm.source,
             "type"     : scm.type,
             "dest"     : scm.dest,
             "version"  : "master",
             "bare"     : "no" }

  ####################################################################
  def _run(self, terms, variables = None, **kwargs):
    scms = []
    terms = [x.lower().replace("redhat", "rhel", 1) for x in terms]
    # Split any existing perforce version spec.
    terms = [x.split(os.path.sep, 1) for x in terms]
    for term in terms:
      distribution = term[0]
      if distribution == "none":
        url = "{0}{1}".format(self._urlPrefix, self._distributionRequest(None))
        if len(term) > 1:
          url = "{0}/...@{1}".format(url, term[1])
        scms.append(self._makeScm(url, variables))
      else:
        dist = Distribution.makeItem(distribution)
        url = "{0}{1}".format(self._urlPrefix, self._distributionRequest(dist))
        if len(term) > 1:
          url = "{0}/...@{1}".format(url, term[1])
        scms.append(self._makeScm(url, variables, dist))

    return [self._makeSpec(scm) for scm in scms]

