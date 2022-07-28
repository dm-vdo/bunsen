# Overview
This document defines, by example, a reformulation of the YAML format for
installation specification used by Bunsen.  

The impetus for this reformulation is two-fold:
  - reduce duplication of specification; e.g., not having to separately 
    provide the same specification for both Fedora28 & Fedora29 
  - allow specification such that Bunsen can at least make an effort to
    provision a never before seen OS distribution based on known requirements 
    for its predecessors

The specification exists not to be formally correct, but to enable achieving
the above.

The second of the above impetuses describes an operational view.  The mechanics
are established in the specification in conjunction with a Bunsen ansible
filter plugin which processes the specification.

# High Level
At the highest level the specification is given a label identifying a list
(allowing specifying order dependency) of dictionaries.  Three dictionary names
are reserved: `common`, `architecture` and `environment`.  Any additional
dictionaries are named based on support for operating system releases.

## Nested Specifications
The first-level dictionaries contained in either `architecture` or
`environment` dictionaries may, in addition to distribution-specific
dictionaries, specify nested `common`, `architecture` and `environment`
dictionaries of their own. This nesting can be repeated to arbitrary depth.

## Terminal Specifications
The terminal specifications, `common` and distribution-specific dictionaries,
are lists of the entities to be installed.  The specific format of these
entities are usage-specific.

## The Reserved Name Dictionaries
### `common`
The `common` dictionary lists entities that are to be installed on *all*
distributions of *all* operating systems. 

```
  - common:
    - <entity>
    - <entity>
    - <entity>
```

### `architecture`
The `architecture` dictionary lists entities to be installed based on a
machine's processor architecture.
```
  - architecture:
    - aarch64:
      - common:
        - <entity>
        - <entity>
        - <entity>
    - ppc64le:
    - s390x:
      - common:
        - <entity>
        - <entity>
        - <entity>
    - x86_64:
```

### `environment`
The `environment` dictionary lists entities to be installed based on criteria
of the environment being provisioned.
```
  - environment:
    - <environment-characteristic>:
      - common:
        - <entity>
        - <entity>
        - <entity>
```

### Distribution-specific Dictionaries
Distribution-specific dictionaries are a list of entities and are named based
on the distributions to which they apply.  *The name is specified as a regex*
and any distribution matching the regex will have the associated entities
installed.

```
  # Common to all Fedora starting with Fedora31.
  - Fedora([1-9][0-9]{2,}|3[1-9]|[4-9][0-9]):
    - <entity>
    - <entity>
    - <entity>
```
# Processing a Specification
As indicated in the 'High Level' section a specification consists of a list of
dictionaries to allow order dependency specification.  The dictionaries are
processed in the order specified at every level of the specification hierarchy.

The Bunsen-provided ansible filter plugin used to process a specification takes
as argument selection criteria composed of the operating system distribution,
machine processor architecture and environmental specifics; e.g.,

```
package_selection:
  distribution: Fedora31
  architecture: aarch64
  environment:
    - python2
```

In practice the values of these selection criteria are determined at ansible
run time.

Note that none of the selection criteria are required; in fact, the entirety of
the selection specification may be empty.  If `architecture` and/or
`environment` are empty or unspecified no entities from the same named
dictionaries in the specification will be selected.  If `distribution`
is empty or unspecified only those entities specified in `common` dictionaries
will be selected.

# Example Specification for Packages
While this example describes the totality (minus nested dictionary
specifications) of a potential specification note that no particular entry must
be specified; nor, if specified, required to have content.
```
package_specification:
  ##########################################################################
  # Architecture-specific.
  ##########################################################################
  - architecture:
    - aarch64:
    - ppc64le:
    - s390x:
    - x86_64:

  ##########################################################################
  # Environment-specific.
  ##########################################################################
  - environment:
    - python2:
      # Common to all RedHat starting with RedHat8.0.
      - RedHat(?![1-7]\.[0-9]+)[1-9][0-9]*\.[0-9]+:
        - python2
        - python2-devel
        - python2-numpy
        - python2-pyyaml
        - python2-setuptools
        - python2-six

  ##########################################################################
  # Fedora
  ##########################################################################
  # Common to all Fedora starting with Fedora32.
  - Fedora([1-9][0-9]{2,}|3[2-9]|[4-9][0-9]):
    - python27

  - Fedora30:
    - python2-libselinux

  - Fedora3[0-1]:
    - python-futures
    - PyYAML

  # Common to all Fedora starting with Fedora31.
  - Fedora([1-9][0-9]{2,}|3[1-9]|[4-9][0-9]):
    - device-mapper-devel

  - Fedora2[8-9]:
    - python-futures
    - python2-filelock
    - python2-libselinux
    - python2-tzlocal
    - PyYAML

  # Common to all Fedora starting with Fedora28.
  - Fedora([1-9][0-9]{2,}|2[8-9]|[3-9][0-9]):
    - ack
    - dkms
    - fedora-repos-rawhide
    - grubby
    - koji
    - ntp
    - python-devel
    - python-pam
    - python-psutil
    - python-setuptools
    - python-six
    - python3-filelock
    - python3-libselinux
    - python3-PyYAML
    - python3-tzlocal

  ##########################################################################
  # RedHat
  ##########################################################################
  - RedHat8\.0:
    - python3-filelock

  # Common to all RedHat starting with RedHat8.0.
  - RedHat(?![1-7]\.[0-9]+)[1-9][0-9]*\.[0-9]+:
    - gcc
    - python3
    - python3-devel
    - python3-libselinux
    - python3-pyyaml
    - python3-setuptools
    - python3-six
    - python3-pyyaml

  - RedHat7\.[7-9]:
    - python3
    - python36-PyYAML

  - RedHat7\.[5-6]:
    - python34

  # Common to all RedHat7 starting with RedHat7.5.
  - RedHat7\.([1-9][0-9]+|[5-9]):
    - libselinux-python
    - ntp
    - python-devel
    - python-filelock
    - python-futures
    - python-pam
    - python-psutil
    - python-setuptools
    - python-six
    - python-tzlocal
    - PyYAML

  # Common to all RedHat starting with RedHat75.
  - RedHat([1-9][0-9]+\.[0-9]+|(7|8)\.([1-9][0-9]+)|7\.[5-9]|8\.[0-9]):
    - dkms

  ##########################################################################
  # Common to all distributions.
  ##########################################################################
  - common:
    - autofs
    - bind-utils
    - emacs
    - git
    - lsof
    - libblkid-devel
    - lz4-devel
    - net-tools
    - nfs-utils
    - pbit-build
    - redhat-lsb-core
    - rsync
    - scam
    - screen
    - smartmontools
    - sshfs
    - tcsh
    - tmux
    - traceroute
    - vim-enhanced
    - xauth
    - xinetd
```
