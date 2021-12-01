#! /usr/bin/env python

from __future__ import print_function

import yaml

from defaults import (Defaults,
                      DefaultsFileContentMissingException,
                      DefaultsFileDoesNotExistException,
                      DefaultsFileFormatException)

#############################################################################
#############################################################################
if __name__ == "__main__":
  # Non-existent file.
  try:
    defaults = Defaults("./defaults/non-existent-file.yml")
  except DefaultsFileDoesNotExistException:
    pass

  # File missing highest-level 'defaults'.
  try:
    defaults = Defaults("./defaults/bad-defaults-no-defaults-key.yml")
  except DefaultsFileFormatException:
    pass

  # File that results in a non-dictionary in-memory representation.
  try:
    defaults = Defaults("./defaults/bad-defaults-non-dictionary.yml")
  except DefaultsFileFormatException:
    pass

  # Corredctly formatted defaults.
  defaults = Defaults("./example-defaults.yml")

  assert defaults.content(["global1"]) == "some-global-value"

  subgroup1 = defaults.content(["group1", "subgroup1"])
  assert subgroup1 is not None
  assert defaults.content(["value1"], subgroup1) == "value111"
  try:
    defaults.content(["non-existent-value"], subgroup1)
  except DefaultsFileContentMissingException:
    pass

  assert defaults.content(["group2", "subgroup1", "value1"]) == "value211"
  try:
    defaults.content(["group2", "subgroup1", "non-existent-value"])
  except DefaultsFileContentMissingException:
    pass

  # Successfully passed.
  print("success")
