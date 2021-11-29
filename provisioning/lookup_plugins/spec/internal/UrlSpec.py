from .Spec import Spec

class UrlSpec(Spec):
  ####################################################################
  # Overridden methods
  ####################################################################
  def _run(self, terms, variables = None, **kwargs):
    return [self._makeSpec(scm)
            for scm in [self._makeScm(url, variables) for url in terms]]
