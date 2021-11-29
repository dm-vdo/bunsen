#! /usr/bin/env python

from __future__ import print_function

from distribution import Distribution, FactoryShell

#############################################################################
#############################################################################
if __name__ == "__main__":
  shell = FactoryShell(Distribution)
  shell.printChoices()

  print("\nDefault distribution: {0}".format(
        Distribution.defaultDistribution().name()))
  print("Default distribution beaker name: {0}".format(
        Distribution.defaultDistribution()(None).beakerName))

  print("\nRoots:")
  print("\tDefault ({0}):".format(Distribution.defaultCategory()))
  for released in Distribution.choices():
    distribution = released(None)
    print("\t\t{0}: {1}".format(distribution.name(), distribution.repoRoot))

  print("\n\tLatest:")
  for latest in Distribution.choicesLatest():
    distribution = latest(None)
    print("\t\t{0}: {1}".format(distribution.name(), distribution.repoRoot))

  print("\n\tNightly:")
  for nightly in Distribution.choicesNightly():
    distribution = nightly(None)
    print("\t\t{0}: {1}".format(distribution.name(), distribution.repoRoot))

  print("\nSpecial Roots:")
  for released in Distribution.choices():
    distribution = released(None)
    print("\t\t{0}: {1}".format(distribution.name(),
                                distribution.specialRepoRoots))

  print("\nDefault UDS:")
  for released in Distribution.choices():
    distribution = released(None)
    print("\t{0}: {1}".format(distribution.name(), distribution.defaultUdsUri))

  print("\nDefault VDO:")
  for released in Distribution.choices():
    distribution = released(None)
    print("\t{0}: {1}".format(distribution.name(), distribution.defaultVdoUri))
