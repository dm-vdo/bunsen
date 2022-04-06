DOCUMENTATION = """
  lookup: latest_repo_roots
  author: Joe Shimkus <jshimkus@redhat.com>
  version_added: "0.1"
  short_description: return uris for latest distribution/architecture
                      pairings
  description:
    - This lookup returns the latest uris for specified
      distribution/architecture pairings.
  arguments:
    - _terms: a list of strings specifying distribution/architecture pairings;
              e.g.; rhel82/x86_64, redhat82/aarch64 or fedora31/s390x
  notes:
    - none
"""
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from discovery.distributions import Distribution

class LookupModule(LookupBase):
  def run(self, _terms, variables = None, **kwargs):
      if len(_terms) == 0:
        raise AnsibleError("incorrect number of arguments")
      pairings = [x.split("/") for x in [x.lower() for x in _terms]]
      invalids = list(filter(lambda x: len(x) != 2, pairings))
      if len(invalids) != 0:
        raise AnsibleError("incorrectly formatted arguments")
      pairings = [[x.replace("redhat", "rhel", 1), y] for (x, y) in pairings]

      return [Distribution.makeItemLatest(distribution,
                                          architecture = arch).repoRoot
              for (distribution, arch) in pairings]
