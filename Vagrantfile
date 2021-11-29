# -*- mode: ruby -*-
# vi: set ft=ruby :

require 'yaml'

$LOAD_PATH << File.join(File.dirname(__FILE__), "bin", "ruby")
require "bunsenConfig"
require "bunsenUtils"
require "virtualBox"

# We occasionally see confusion from Ansible subprocesses if we let Vagrant
# launch them concurrently, due to some race condition. Worse, the Ansible
# processes don't get any synchronization -- we can start ansible-playbook
# against a VM that'll run an NFS client while we're still downloading a box to
# bring up the NFS server VM. Serialize things to keep it
# sane. Unfortunately(?), this applies to building the VMs themselves, not just
# to the provisioning.
ENV['VAGRANT_NO_PARALLEL'] = 'x'

# Get a handle to the virtualbox bash script.
virtualBoxShell = File.join(File.dirname(__FILE__),
                            "bin", "bash", "virtualBox.sh")

# Check for the plugins we'll be using.
["vagrant-hosts", "vagrant-host-shell"].each do |plugin|
  BunsenUtils.assert_plugin_exists(plugin)
end

# Load the configuration file.
CONFIG = BunsenConfig.configure()
VIRTUAL_BOX = VirtualBox.new(BunsenConfig::LOCAL_DIR, BunsenConfig::USER_DIR)

# The actual configuration.
Vagrant.configure("2") do |config|
  if defined?(PROXY_URL) && (PROXY_URL != "")
    BunsenUtils.assert_plugin_exists("vagrant-proxyconf")
    config.proxy.http     = PROXY_URL
    config.proxy.https    = PROXY_URL
    config.proxy.no_proxy = "localhost,127.0.0.1"
  end

  # Define a lambda that sets up the common portions of a libvirt machine.
  libvirt_machine_common = lambda do |libvirt, config, machine|
    config.vm.box_version = machine.dig("box", "version")
    config.vm.box_url = machine.dig("box", "url")

    # This option, turned on in Fedora 30, is currently incompatible with disks
    # -- see github issue
    # https://github.com/vagrant-libvirt/vagrant-libvirt/issues/1072 .
    # However, pre-2.2 (e.g., in Fedora 29), the option wasn't supported, so we
    # can't unconditionally set it.
    req = Gem::Requirement.new(['>= 2.2'])
    if req.satisfied_by?(Gem::Version.new(Vagrant::VERSION))
      libvirt.qemu_use_session = false
    end
    libvirt.random_hostname = true
    libvirt.cpus = machine["cpus"]
    libvirt.memory = machine["memory"] * 1024
    # Establish a communication channel for the QEMU guest agent so it can
    # resync time on waking a host laptop from sleep, etc.
    libvirt.channel :type => 'unix',:target_name => 'org.qemu.guest_agent.0',
                    :target_type => 'virtio'

    machine["disks"].each do |disk|
      libvirt.storage :file, :size => "#{disk['size']}G" , :type => 'raw'
    end
  end

  # Define a lambda that sets up the common portions of a virtualbox machine.
  virtualbox_machine_common = lambda do |virtualbox, config, machine|
    hostname = machine["name"]
    info = VIRTUAL_BOX.get_info(hostname)
    instanceIdentifier = info['id']
    config.vm.box_version = machine.dig("box", "version")
    config.vm.box_url = machine.dig("box", "url")
    config.vm.network "private_network", ip: info['ip']

    virtualbox.name = instanceIdentifier
    req = Gem::Requirement.new(['>= 1.8'])
    if req.satisfied_by?(Gem::Version.new(Vagrant::VERSION))
      virtualbox.linked_clone = true
    end
    virtualbox.cpus = machine["cpus"]
    virtualbox.memory = machine["memory"] * 1024
    virtualbox.customize ["modifyvm", :id,
                          "--audio", "none",
                          "--macaddress1", "auto"]

    sizes = machine["disks"].map {
      |disk|
      disk["size"]
    }.join(" ")
    config.vm.provision :host_shell do |hs|
      hs.inline = "#{virtualBoxShell} virtualBoxProvision" +
                    " #{instanceIdentifier} #{sizes}"
    end
  end

  ansible_host_vars = {}

  CONFIG["machines"].machines.each do |machine|
    name = machine["name"]
    config.vm.define name do |instance|
      instance.vm.hostname = name
      instance.vm.box = machine.dig("box", "name")

      # libvirt specification.
      instance.vm.provider :libvirt do |libvirt, config|
        libvirt_machine_common.call libvirt, config, machine
      end

      # virtualbox specification
      instance.vm.provider :virtualbox do |virtualbox, config|
        virtualbox_machine_common.call virtualbox, config, machine
      end

      # Common setup.
      instance.vm.synced_folder ".", "/vagrant", type: "nfs", nfs_udp: false,
                                disabled: true

      instance.vm.provision :hosts, :sync_hosts => true

      ansible_host_vars[name] = machine.ansible_host_vars

      instance.vm.provision :ansible, run: "always" do |ansible|
        # Use root by default, since we're running mostly stuff that requires
        # it.
        ansible.become = true
        ansible.host_vars = ansible_host_vars
        ansible.groups    = CONFIG.ansible_groups
        ansible.playbook  = File.join("provisioning", "dummy.yml")
      end
    end
  end
end
