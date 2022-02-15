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
* `dnf install python3-distributions`

Regardless of the method of installation you choose the following software will
be installed to satisfy dependencies of `python3-distributions`:
* bunsen support
  * `python3-architectures`
  * `python3-command`
  * `python3-defaults`
  * `python3-factory`
  * `python3-repos`
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

<!-- links -->
[bunsen]: <insert url>


<!-- begin comment
     Below here is old README content.  This needs to be updated.
     It is commented out to prevent its rendeering


## Things You'll Need Installed
* ansible
* bunsen support
  * python-distributions
* python modules
  * requests
* virtual machine; one or both of:
  * libvirt and qemu
  * virtualbox
* vagrant support
  * vagrant
  * vagrant plugins:
    * vagrant-libvirt (if using libvirt)
    * vagrant-hosts
    * vagrant-host-shell
* HTTP access to file.rdu.redhat.com for the default boxes

## System/user preparation
  * Linux
    * CSB (RHEL 7.x)
      ```
      sudo yum install ansible git vagrant gcc ruby-devel virt-manager \
        libvirt{,-devel,-python,-client} qemu{,-kvm,-img} python-virtinst \
        <python-requests>
      vagrant plugin install vagrant-libvirt
      ```

    * CSB (RHEL 8.x)
      ```
      sudo yum install ansible git vagrant gcc ruby-devel virt-manager \
        libvirt{,-devel,-client} qemu{,-kvm,-img} python3-libvirt \
        virt-install
      vagrant plugin install vagrant-libvirt
      ```
    
    * stock RHEL 8.x
      [TBD?]

    * Fedora 28
      ```
      sudo dnf install ansible git vagrant{,-libvirt} libvirt{,-libs} \
        @vagrant @virtualization <python-requests>
      for service in nfs nfs3 rpc-bind mountd; do
        sudo firewall-cmd --add-service=${service} --permanent
      done
      sudo firewall-cmd --reload
      ```

    * Fedora 29
      [TBD?]

    * Fedora 30
      ```
      sudo dnf install ansible git ruby-devel libxml2-devel \
      libvirt{,-libs,-devel} @vagrant @virtualization
      ```
	  
    * Fedora 31, 32
      There's a version incompatibility between the vagrant-libvirt RPM package
      and some of the vagrant plugins that we install, where Fedora provides
      one version of a supporting package, and the plugins require another
      version of the same supporting package. Thus, we need to install
      vagrant-libvirt through the vagrant plugin interface, not as an RPM
      package.

      The package group @vagrant includes the vagrant-libvirt support, which is
      later removed because of the version incompatibility. We could just
      install the vagrant package by itself, but it recommends the libvirt
      support so by default that gets installed anyway unless we explicitly
      exclude it. Also, if you update from Fedora 30, and had previously
      installed vagrant and the libvirt support, you'll still need to remove
      the latter. For simplicity we just show always doing the removal below.

      ```
      sudo dnf install ansible git gcc make redhat-rpm-config \
      ruby-devel libxml2-devel libvirt{,-libs,-devel} \
      @vagrant @virtualization
      sudo dnf remove vagrant-libvirt
      vagrant plugin install vagrant-libvirt
      ```

    * Common
      Set `SELINUX` in `/etc/selinux/config` to `disabled`

      ```
      vagrant plugin install vagrant-hosts vagrant-host-shell
      sudo systemctl enable libvirtd
      sudo gpasswd -a ${USER} libvirt
      sudo reboot
      ```

  * macOS
    * ansible: macports (`https://www.macports.org`)
    * python modules:
      * requests: macports (`https://www.macports.org`)
      * yaml:
        * The macports ansible installation automatically installs a version of
          yaml.  The easiest way to utilize this is to activate the python version
          that macports also installed;
          e.g., `sudo port select --set python python27`.
          To go back to the Apple provided version of python execute the
          following:
          `sudo port select --set python none`.
    * vagrant: `https://www.vagrantup.com/downloads.html`
    * vagrant plugins: `sudo vagrant plugin install vagrant-hosts vagrant-host-shell`
    * virtualbox: `https://www.virtualbox.org`

  * Windows
    * ansible: ?
    * python modules:
      * requests: ?
      * yaml: ?
    * vagrant: `https://www.vagrantup.com/downloads.html`
    * virtualbox: `https://www.virtualbox.org`

  &nbsp;&nbsp;
  Notes
  1. The virtualbox configuration currently uses a hack to dynamically set
    specific IP addresses.  A less hacky solution is to be hoped for.
  2. If you get the error
       no such name (https://gems.hashicorp.com/specs.4.8.gz)
    then just wait a minute and try again. This isn't an uncommon occurrence.


# I. Using The Vagrant Set Up

  1. Prepare your host system as described in "Setting Up Your Host System."
  2. Create and populate a perforce workspace including
      `//eng/main/src/tools/bunsen`. Or check it out from git:
      `git clone git://git.engineering.redhat.com/users/awalsh/main.git`
  3. `cd <workspace>/main/src/tools/bunsen`.
  4. `vagrant up`
  5. `./vagrant-run-ansible [--extra-vars="install_bunsen_support=1"]`

  &nbsp;&nbsp;
  Notes
  1. Ansible provisions machines in parallel, which can create heavy load on
      the host during parts of the Ansible run. Specifying `-f 1` to
      vagrant-run-ansible will reduce the parallelism to 1 machine at a time,
      lessening peak load at the cost of a longer provisioning process.
  2. The above will create a default lfarm-like set of machines, based on the
      default vagrant bunsen configuration.
  3. Using vagrant-run-ansible will create the directory `~/.bunsen` containing
      configuration data.  You may add to this directory the file
      `vagrant-config.yml`.  If it exists its contents will be used to
      override, as well as extend, the configuration across all of your
      vagrant bunsen environments.
  4. Additionally you may also have a `vagrant-config.yml` file in a specific
     vagrant bunsen environment (e.g., `<workspace>/main/src/tools/bunsen`)
     in which case its contents will override, as well as extend, the
     configuration for that specific environment.
  5. See `<workspace>/main/src/tools/bunsen/example-user-vagrant-config.yml`
     for specifics on the config file options.
  6. If the "find public keys" step fails in the following fashion:
       ```
       TASK [known_host : Fetch SSH public key(s)] *****************
       fatal: [server]: FAILED! => {"changed": false,
       "cmd": ["ssh-keyscan", "-4", "192.168.121.1"],
       "delta": "0:00:00.005029", "end": "2020-04-29 21:14:20.652756",
       "msg": "non-zero return code", "rc": 1,
       "start": "2020-04-29 21:14:20.647727",
       "stderr": "write (192.168.121.1): Connection refused\r\n
       write (192.168.121.1): Connection refused\r\n
       write (192.168.121.1): Connection refused",
       "stderr_lines": ["write (192.168.121.1): Connection refused",
       "write (192.168.121.1): Connection refused",
       "write (192.168.121.1): Connection refused"],
       "stdout": "", "stdout_lines": []}

     you might not have SSH running on the
     host machine. Start it with `sudo systemctl start sshd`. If that doesn't
     work, you may have a firewall issue; investigate `iptables -L LIBVIRT_FWI`
     and `iptables -L LIBVIRT_FWO`, you may need to add iptables rules to
     allow traffic to/from your VMs.
     `sudo iptables -I LIBVIRT_FWO -s "192.168.121.0/24" -m state --state NEW -j ACCEPT`
     may help, but without knowing what iptables rules already exist, this
     can be dangerous.

  7. Solving dependency hell:
     You may observe that using the vagrant packages from repository (in
     Fedora) could introduce dependency/version problems with installing the
     plugins required for Bunsen.

     An example of this behavior:
     ```
     $ vagrant plugin install vagrant-hosts vagrant-host-shell
     Installing the 'vagrant-hosts' plugin. This can take a few minutes...
     Vagrant failed to properly resolve required dependencies. These
     errors can commonly be caused by misconfigured plugin installations
     or transient network issues. The reported error is:

     conflicting dependencies json (= 1.8.3) and json (= 2.2.0)
       Activated json-2.2.0
       which does not match conflicting dependency (= 1.8.3)

       Conflicting dependency chains:
         json (= 2.2.0), 2.2.0 activated

       versus:
         json (= 1.8.3)

       Gems matching json (= 1.8.3):
         json-1.8.3
     ```
     Other package:plugin combinations that also showed issues:
     ```
     vagrant-libvirt - Encounters errors with fog-core
     ```

     a. You could use the Centos 64-bit variant of vagrant. 
        Remove the `vagrant` and `vagrant-libvirt` packages and download the
	Centos 64-bit variant of Vagrant from 
	https://www.vagrantup.com/downloads.html.  This
       issue was originally observed on Fedora 30, but may affect more than just
       that OS/Release.  This issue was specifically resolved on Fedora 30 with
       this method.

     b. You can also try uninstalling the vagrant-libvirt package, and install
        it via `vagrant plugin install vagrant-libvirt` instead; sweettea used
	this to resolve the fog-core issue on Fedora 31.

  8. If you are using an FAI installed variant of Fedora 30 (and likely other
     releases), the permissions of `/etc/polkit-1/rules.d` and
     `/usr/share/polkit-1/rules.d` may be set incorrectly.  The permissions for
     both of these locations should be owned by root:root with 0755 modes.

     The error message resembled:
       ```
       Error while connecting to libvirt: Error making a connection to libvirt URI qemu:///system?no_verify=1&keyfile=/permabit/user/awalsh/.ssh/id_rsa:
       Call to virConnectOpen failed: authentication unavailable: no polkit agent available to authenticate action 'org.libvirt.unix.manage'
       ```
     The fix can be implemented by running these commands:
       ```
       sudo chown root.root /etc/polkit-1/rules.d /usr/share/polkit-1/rules.d
       sudo chmod 0755 /etc/polkit-1/rules.d /usr/share/polkit-1/rules.d
       sudo systemctl restart libvirtd
       sudo systemctl restart polkit
       ```

  &nbsp;&nbsp;
  **Important**
  * macOS filesystems, by default, are not case-sensitive (although they are
    case-preserving).  This is an issue for builds, such as vdo, that generate
    artifacts whose names differ only in case in the same directory.

    There are a number of ways to resolve/workaround this:
      1. reformat the Mac's disk as case-sensitive
      2. use an additional storage device which is formatted case-sensitve
      3. use `Disk Utility` on macOS to create a disk image that is
          case-sensitive and mount this image

      In cases 2. & 3. the mounted image can be found in `/Volumes` and added
      to the config file for sharing.

# III. Using Ansible With Beaker Systems

  Set your Beaker preferences so that machines you reserve are configured to
  let you log in as root with your ssh key.

  Reserve three or more machines from Beaker, with the beaker-client
  package installed:
  ```
    bkr workflow-simple --task=/distribution/reservesys --distro=RHEL-7.7 \
      --arch=x86_64 --variant=Server \
      --keyvalue "DISKSPACE > 240000" \
      --keyvalue "DISK_CONTROLLER != megaraid_sas" \
      --keyvalue "DISK_CONTROLLER != mptsas" \
      --keyvalue "BOOTDISK != megaraid_sas" \
      --keyvalue "BOOTDISK != mptsas"
  ```

  Explanation of options:
   * task=/distribution/reservesys means to reserve the machine for you after
     the initial OS installation task is completed.
   * distro=RHEL-7.7 should be obvious
   * arch=x86_64 also
   * variant=Server isn't terribly important, it should work fine if you start
     off with the Client or Workstation variant as well.
   * DISKSPACE>240000 specifies the minimum disk space requirement
   * DISK_CONTROLLER!=megaraid_sas is because our Perl scripts make some
     assumptions about the configurations of machines with MegaRAID controller
     cards.
   * DISK_CONTROLLER!=mptsas is because these controllers seem to confuse the
     smartd daemon.
   * BOOTDISK --keyvalue options are specified as not all Beaker systems report
      megaraid and/or mptsas in DISK_CONTROLLER

  Other architectures: aarch64, ppc64le, s390x.

  Other distro values:
   * RHEL-7.8
   * Fedora-31, variant "Everything" or "Server"
   * prerelease RHEL 8 uses datestamp, e.g., RHEL-8.0-20181030.n.0, and variant
     "BaseOS"
   * RHEL8.0 is "RHEL-8.0.0"

  Additional options:
   * Extend reservation from default time up to 99 hours with "--taskparam
     RESERVETIME=356400".
   * Add notes to be displayed on Beaker web pages with
     "--whiteboard=some-text-here".

  There's an alternate way you can reserve some distributions, based on tags
  attached to specific builds. If you specify `--family=RedHatEnterpriseLinux8
  --tag=RTT_PASSED` instead of `--distro=...`, then you'll get the latest build
  of RHEL 8 that has passed certain automated tests; specify tag
  `RTT_ACCEPTED`, and you'll get the latest build of RHEL 8 that has passed
  some further acceptance testing.

  N.B.: Installation of the operating system may fail under Beaker. If this
  happens, your job will be terminated and you'll need to resubmit it.

  After Beaker notifies you that your machines are available, create an
  inventory file, assigning roles, and specifying the "root" account for
  logging in.
  
  If you wish (or need, depending on farm machine storage availability) to
  utilize a machine to provide required storage for farms, list the machine to
  fulfill that role as "storage_server".  This does not have to be an
  additional machine, but can be one of the already allocated machines
  (generally, the infrastructure machine also fulfills this role).  The farms
  will automatically utilize the specified machine.

  If you wish to use any of the farm machines for performance tests you *must*
  assign them to the role "performance_farms".  The "performance_farms" role is
  a superset of the "farms" role.  You do not need to include those systems in
  the "farms" role, though you may wish to do so in order to be able to direct
  ansible to operate against all "farms" including the "performance_farms"
  using `-l farms`.

```
  host1.lab.eng.bos.redhat.com  ansible_user=root
  host2.lab.eng.bos.redhat.com  ansible_user=root
  host3.lab.eng.bos.redhat.com  ansible_user=root
  host4.lab.eng.rdu2.redhat.com ansible_user=root
  host5.lab.eng.rdu2.redhat.com ansible_user=root

  [infrastructure]
  host1.lab.eng.bos.redhat.com
  
  [storage_server]
  host1.lab.eng.bos.redhat.com

  [resources]
  host2.lab.eng.bos.redhat.com

  [farms]
  host3.lab.eng.bos.redhat.com
  host4.lab.eng.rdu2.redhat.com
  host5.lab.eng.rdu2.redhat.com

  [performance_farms]
  host5.lab.eng.rdu2.redhat.com
```

  If a machine is running Fedora 28, add `ansible_python_interpreter=python3`
  to the line in the first section. If a machine is running RHEL 8, add
  `ansible_python_interpreter=/usr/libexec/platform-python`.

  Run Ansible against the inventory file you created, here assumed to
  be "beaker-inventory":

    `ansible-playbook -i beaker-inventory provisioning/playbook.yml`

  You can put one machine in both "resources" and "farms" if you like,
  and use it both for compiling and as a test target system, but you
  are responsible for making sure that you're not doing both at once.

  You can configure a subset of the machines or roles by listing them with a
  `-l` parameter, but the initial configuration of the "infrastructure" machine
  must happen with the first batch.

  The Ansible script will create an account named "bunsen" that you
  can log into using your SSH key, with its own home directory (stored
  on the infrastructure machine and NFS-mounted by the others). It
  will install the Permabit Perl and Python libraries under /permabit
  and create a /permabit/not-backed-up tree shared between the
  machines. An RSVP server will be started on the infrastructure
  machine, and the farm machines will be registered. If the resource
  machine is an x86_64 machine, the Perforce "p4" binary will be
  installed.

  A UDS "jasper" release tree will be checked out and built.

  Shell initialization files will be created in /etc/profile.d to set
  shell variables like UDS_TOP and PRSVP_SERVER.

    KNOWN BUG: The infrastructure box must currently be an x86_64
	system because the RSVP server package is x86-only. However, the
	UDS tree, including the user-mode library against which some VDO
	programs are linked, is compiled on the infrastructure system by
	the Ansible playbook. So, if you're planning to do non-x86
	testing, you'll have to do a "make clean" and "make" in
	/permabit/build/git/uds.git after running the Ansible playbook.

    N.B.: Occasionally the machine description in Beaker may be out of
    sync with the actual hardware, or some hardware has failed, and so
    a machine will be reserved with less disk space than was
    requested. The Ansible playbook includes a check of the available
    disk space; if there isn't enough for its purposes, configuration
    of that machine will fail.

  After the Ansible script finishes, log into the "resources" machine as
  "bunsen", check out your VDO tree, build it and run tests,
  etc. After you've compiled your VDO tree on the "resources" machine, you
  could run the VDO Perl tests from the "infrastructure" machine instead,
  if you've set up your inventory to list the "resources" machine also as
  a "farm" machine; this will allow for more concurrency in testing.

  Use extendtesttime.sh if you need more time on the machine than you
  originally reserved it for; you can extend it to 99 hours from the time you
  run the script, to a maximum of 10 days total (or, reportedly, 3 days for
  POWER 9 machines). Run return2beaker.sh on each machine when you're done with
  it, or use the Beaker web UI or CLI and cancel the job. From another machine,
  you can also use `bkr watchdog-extend --by=<N> <FQDN>` to update the
  reservation times; note that, contrary to the usage message, the command
  specified sets the timeout as a number of seconds from the current time,
  rather than adding that many seconds to the remaining time.

  You may want to mount your permabit home directory from
  nfs-01.permabit.lab.eng.bos.redhat.com:/user. Your UID doesn't match, so
  it will probably be read-only.

  N.B.: Many Beaker machines are configured to boot from the network by
  default, and some of them don't fall back to booting from disk when Beaker
  doesn't respond to the boot request. The "rhts-reboot" program will configure
  machines using EFI to boot from local disk on the next reboot, and then
  immediately reboot them. There isn't a delayed-reboot option akin to
  "shutdown +1", nor a controlled-crash option, but rhts-reboot is a simple
  script using the "efibootmgr" program and should be easy to adapt.

  See https://home.corp.redhat.com/wiki/conserver for information on accessing
  the consoles of Beaker systems.

  Some failure modes we've seen in Beaker configurations:
  * Beaker can't install OS on machine cleanly
  * on boot, DHCP client gets no response from server
  * DHCP lease expires, server has gone offline, DHCP client doesn't switch to
    broadcast, never gets lease renewed, takes IPv4 interface offline
  * routers advertise IPv6 support but routes are incomplete so connections
    have to time out (but disabling IPv6 might break some parts of Beaker
    service)
  * hardware doesn't match inventory; not enough local disk space for tests

  If you can't get enough local storage on Beaker farm systems, specifying a
  machine in the [storage_server] section of the inventory file will result in
  that machine being provisioned as a storage server and automatically utilized
  by the farm systems for storage.  The farm systems will contact a targetd
  daemon (using user "admin", password "permabit0") on the named server to
  create an iSCSI LUN for the farm to use for its `/u1` and `vdo_scratch`
  storage, instead of using local disk space.  Using storage over the network
  will make tests run more slowly, of course.

  For machines with special devices to be used for VDO testing (e.g., NVMe
  storage), a test device can be specified in the inventory file with a
  per-host variable test_storage_device giving the basename of the device in
  /dev:
  
```
  vdo-storage-01.lab.eng.bos.redhat.com ... test_storage_device=nvme0n1
```

  Local or iSCSI storage will still be used for the `/u1` storage.

# IV. Using jug
  `jug` is a python command line utility that provides automation of the tasks
  described in Section III and more.  `jug` can be installed for use via:
  
      (vis=vdo-image-store.permabit.lab.eng.bos.redhat.com && \
       pip install --user --upgrade \
		               --extra-index-url http://${vis}/repository/python-pip-repo \
		               --trusted-host ${vis} \
		               python-jug)

  The default behavior of `jug` is to generate the XML directing Beaker in the
  tasks to perform and print this to stdout.  If your system has the Beaker
  command line installed `jug` can directly submit the job to Beaker. 
  Alternatively, you can redirect the output to a file and upload that file at
  the Beaker web site, `https://beaker-server.host.prod.eng.bos.redhat.com`.

  `jug` provides the following deveopment- and test-related Beaker job XML
  generation:
  * `test-machine`: installs an OS and kernel on machines suitable for uds/vdo
  * `provision`: creates an environment analogous to a development workstation
    with lfarms
  * `uds-build`: same as `provision` but clones and builds the latest uds
  * `uds-test`: same as `uds-build` but runs specified tests
  * `vdo-build`: same as `provision` but clones and builds the latest vdo
  * `vdo-test`: same as `vdo-build` but runs specified tests

  With the exception of the `*-test` jobs all the systems allocated are 
  reserved at the end of the job for one day; you can change this using the
  `jug` `--reserve` option. The `*-test` jobs will reserve the systems
  *if any of the specified tests fail* else the systems will be released back
  to Beaker at the end of the job.  Using `--reserve` will override this
  behavior and reserve the systems for the specified duration.

  `jug` has many options.  Run `'jug --help'` and `jug <job> --help'` to learn
   more.

  &nbsp;&nbsp;
  Notes
  1. Beaker's XML validation has a bug with tasks that have parameter
     subelements.  Consequently, you will get a warning from Beaker when
     submitting the job. Using `jug` to submit the job directly
     will submit the job regardless of the warning.  The Beaker website will
     require an additional confirmation of job submission.

end comment -->
