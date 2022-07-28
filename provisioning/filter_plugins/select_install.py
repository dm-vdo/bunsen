# Custom jinja2 filter select_install(specification, selection).

# Inputs are:
#   specification:  an installation options specification
#   selection:      attributes to use in selecting from the specification
#
# Example selection:
#   { "distribution" : "RedHat81",
#     "architecture" : "s390x",
#     "environment"  : ["python2"] }
#
# None of the selection values are required, though without distribution the
# list of selections returned will be only those common to all distributions,
# if identified, from the specification.

import re

#############################################################################
def _select_install(specification, distribution, architecture,
                    environment = []):
  if specification is None:
    specification = []

  selected = []

  for specificationDict in specification:
    # Each specificationDict has only one key.  This is a consequence of the
    # specification format requiring processing of entries in order allowing
    # for multiple entries to be specified in dependence order.
    key = list(specificationDict.keys())[0]

    # Architecture-specific specification.
    if key == "architecture":
      if (architecture is not None) and (specificationDict[key] is not None):
        arches = dict([(list(d.keys())[0], d[list(d.keys())[0]])
                        for d in specificationDict[key]])
        try:
          selected.extend(_select_install(arches[architecture],
                                          distribution,
                                          architecture,
                                          environment))
        except KeyError:
          # No such architecture.
          pass
      continue

    # Distribution-independent specification.
    if key == "common":
      if specificationDict[key] is not None:
        selected.extend(specificationDict[key])
      continue

    # Environment specification.
    if key == "environment":
      if specificationDict[key] is not None:
        environ = dict([(list(d.keys())[0], d[list(d.keys())[0]])
                        for d in specificationDict[key]])
        for criterion in environment:
          try:
            selected.extend(_select_install(environ[criterion],
                                            distribution,
                                            architecture,
                                            environment))
          except KeyError:
            # No such criterion.
            pass
      continue

    # Distribution-specific specification.
    if distribution is not None:
      if ((specificationDict[key] is not None)
          and (re.search(key, distribution) is not None)):
        selected.extend(specificationDict[key])
      continue

  return selected

#############################################################################
def select_install(specification, selection):
  if selection is None:
    selection = {}

  try:
    distribution = selection["distribution"]
  except KeyError:
    distribution = None

  try:
    architecture = selection["architecture"]
  except KeytError:
    architecture = None

  try:
    environment = selection["environment"]
  except KeyError:
    environment = None

  if environment is None:
    environment = []

  return _select_install(specification, distribution, architecture,
                         environment)

#############################################################################
# Incorporate the filters in the execution space.
class FilterModule(object):
    def filters(self):
        return { 'select_install' : select_install }
