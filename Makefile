# $Id: //eng/main/src/tools/bunsen/Makefile#1 $

SUBDIRS :=

RANDOM_HEX_NUMBER = $(shell hexdump -n 8 -v -e '/1 "%02X"' /dev/urandom)

INFRASTRUCTURE := check-fedora-server-$(RANDOM_HEX_NUMBER)
FEDORA_BUILDER := check-fedora-builder-$(RANDOM_HEX_NUMBER)
FEDORA_FARM    := check-fedora-farm-$(RANDOM_HEX_NUMBER)
RHEL_BUILDER   := check-rhel-builder-$(RANDOM_HEX_NUMBER)
RHEL_FARM      := check-rhel-farm-$(RANDOM_HEX_NUMBER)

all .DEFAULT:
	set -e; for dir in ${SUBDIRS}; do \
	  ${MAKE} -C $$dir $@; \
	done

checkin: vagrant-config.yml
	set -e; for dir in ${SUBDIRS}; do \
	  ${MAKE} -C $$dir $@; \
	done
	@vagrant up `cat ./vagrant-check-machines`
	@./vagrant-run-ansible -l "`cat ./vagrant-check-machines`"

clean:
	for dir in ${SUBDIRS}; do \
	  ${MAKE} -C $$dir $@; \
	done
	if [ -e ./vagrant-check-machines ]; then \
	  vagrant destroy -f `cat ./vagrant-check-machines`; \
	fi
	rm -f ./vagrant-check-machines
	rm -f ./vagrant-config.yml

vagrant-check-machines:
	echo "$(INFRASTRUCTURE) $(FEDORA_BUILDER)-1 $(FEDORA_FARM)-1 \
			$(RHEL_BUILDER)-1 $(RHEL_FARM)-1" > ./$@

vagrant-config.yml: vagrant-check-machines
	echo "$$VAGRANT_CONFIG" > ./$@

define VAGRANT_CONFIG
---
machines:
  # Override the default infrastructure server.
  server:
    count: 0

  # The check-in environment.
  $(INFRASTRUCTURE):
    distro: fedora30
    role: infrastructure
    count: 1

  $(FEDORA_BUILDER):
    distro: fedora30
    role: resources
    count: 1

  $(FEDORA_FARM):
    distro: fedora30
    role: farms
    count: 1

  $(RHEL_BUILDER):
    distro: rhel82
    role: resources
    count: 1

  $(RHEL_FARM):
    distro: rhel82
    role: farms
    count: 1
endef
export VAGRANT_CONFIG

