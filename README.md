# I. Bunsen
`bunsen` is a collection of `ansible` entities that will provision a 
user-provided set of systems (physical and/or virtual) as a simulacrum of the
official `VDO` development environment.  In this way you the user is able to
take advantage of the tools, tests, etc. in the same way as the mainstream 
development team.

The basic environment established by `bunsen` consists of:
* One "infrastructure" system (server for other systems)
* One or more "builder" systems (development systems)
* One or more "farm" systems (testing targets)

# II. Getting `bunsen`
As you're reading this README you may already have `bunsen`.  Or, perhaps, 
someone has provided you with this README in which case `bunsen` can be 
acquired from this location [bunsen].

# III. Setting Up A Controller System

In order to use `bunsen` you will require a system to function as an `ansible`
controller.  To that end you will need to install `ansible` on some system.
Additionally you will require `bunsen` runtime support code on that same
system.

## III.1 ansible
See your system vendor for `ansible`.

## III.2 bunsen support
There are two ways get the necessary `bunsen` support software.  The simplest
is to let `bunsen` install it for you.  This is accomplished by overriding the
default setting of the `install_bunsen_support` variable when invoking the
`bunsen` playbook by providing the following additional argument to 
`ansible-playbook`:
* `--extra-vars="install_bunsen_support=true"`  

You need only provide this additional argument the first time you
run the `bunsen` playbook on an `ansible` controller or if you want `bunsen` to
install available updates to the support software.

The second way to get the `bunsen` support software is to install it yourself.
For this you will want to execute the following commands:
* `dnf copr enable <name>/<repo>`
* `dnf install python3-resource-discovery`

Regardless of the method of installation you choose the following software will
be installed to satisfy dependencies of `python3-resource-discovery`:
* bunsen support
  * `python3-utility-mill`
* system supplied (if not already installed)
  * `pyyaml` 

## III.3 hostname resolution
Hosts in the `bunsen` environment must be able to reach each other by hostname. 
`bunsen` can provision an environment provided by `vagrant` and take advantage 
of its automatic handling of ssh connections (via `vagrant ssh`) by modifying 
the ~/.ssh/config file to proxy through that command. This would allow for you 
to ssh into the provisioned machines from the host directly as yourself.

You can enable this behavior by providing the following additional argument to 
`ansible-playbook`:
* `--extra-vars=enable_proxy_vagrant_ssh_config=true"`  

