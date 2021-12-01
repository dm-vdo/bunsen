#! /usr/bin/env python

from __future__ import print_function

from factory import Factory
from FactoryShell import FactoryShell

#############################################################################
#############################################################################
if __name__ == "__main__":
  shell = FactoryShell(Factory)
  shell.printChoices()
  shell.run()
