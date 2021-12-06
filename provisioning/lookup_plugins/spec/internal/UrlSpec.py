from .Spec import Spec

class UrlSpec(Spec):
  ####################################################################
  # Overridden methods
  ####################################################################
  def _run(self, terms, **kwargs):
    return [self._makeSpec(scm)
            for scm in [self._makeScm(url) for url in terms]]
