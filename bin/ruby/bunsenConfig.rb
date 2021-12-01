require 'pp'
require 'yaml'

require 'mergeable'

module BunsenConfig
  class << self
    attr_accessor :debug
  end

  BunsenConfig.debug = {}

  LOCAL_DIR = File.expand_path("../..", File.dirname(__FILE__))
  USER_DIR  = File.join(Dir.home, ".bunsen")
  if !File.exist?(USER_DIR)
    Dir.mkdir(USER_DIR)
  end

  ##########################################################################
  # Base class for all configuration hashes. YAML hashes are all converted to
  # ConfigHashes which behave as hashes where each field can have its own merge
  # policy.
  ##########################################################################
  class ConfigHash < MergeableHash
    attr_accessor :_prepared

    ##########################################################################
    # Perform any additional work once all merges are complete.
    #
    # @param config  The top-level config which has been merged.
    ##
    def post_merge(config)
      if not self._prepared
        self.prepare(config)
        self._prepared = true
      end
    end

    ##########################################################################
    # Prepare a ConfigHash for use. This method does the actual post merge
    # work. It should only be called from post_merge() which ensures that it
    # is only called on a given ConfigHash once.
    #
    # @param config  The top-level config which has been merged.
    ##
    def prepare(config)
      # by default, nothing to do
    end
  end

  ############################################################################
  # The top level bunsen configuration
  ############################################################################
  class Config < ConfigHash
    self.set_converters(converters:
                          { "environment"   => "BunsenConfig::Environment",
                            "role_defaults" => "BunsenConfig::RoleDefaults",
                            "machines"      => "BunsenConfig::Machines",
                          });

    ########################################################################
    # Load a list of YAML files and merge them into a Config.
    #
    # @param paths  The name of the YAML files to merge
    #
    # @return a Config which was loaded from the specified files and is
    #         ready for use
    ##
    def self.load(*paths)
      config = Config.new()
      paths.select { |path|
        File.file?(path)
      }.each do |path|
        if BunsenConfig.debug[:load]
          puts "loading #{path}"
        end
        config.merge!(Config.new(path))
      end

      config.post_merge(config)
      config
    end

    ##########################################################################
    # Initializer.
    #
    # @param path  The path to the YAML file to load in order to populate this
    #              config; if nil, the config will be empty
    ##
    def initialize(path=nil)
      super(path.nil? ? path : YAML.load_file(path))
    end

    ##########################################################################
    # Prepare a Config for use after all merges are complete.
    ##
    def prepare(config)
      self["environment"].post_merge(config)

      if self["machines"].nil?
        raise "No machines!"
      end

      self["machines"].post_merge(config)
    end

    ##########################################################################
    # Get the ansible groups for this configuration.
    #
    # @return The ansible groups for this configuration
    ##
    def ansible_groups()
      if not @ansible_groups
        @ansible_groups = self["machines"].ansible_groups
        @ansible_groups["all:vars"] = self["environment"].ansible_groups
      end

      @ansible_groups
    end
  end

  ##########################################################################
  # The environment
  ##########################################################################
  class Environment < ConfigHash
    self.set_converters(converters:
                          { "mounts"               => "MergeableArray",
                            "user-mounts"          => "Accumulator",
                            "name_prefix"          => "MergeableString",
                            "domain"               => "MergeableString",
                            "user_account"         => "MergeableString",
                            "use_permabit_account" => "MergeableBoolean",
                          })

    ##########################################################################
    # @inherit
    ##
    def prepare(config)
      self["mounts"].push(*self["user-mounts"]).each { |mount|
        mount["source"] = File.expand_path(mount["source"])
      }
    end

    ##########################################################################
    # @inherit
    ##
    def ansible_groups()
      if not self._prepared
        raise "Unprepared to generate ansible groups"
      end

      deploying_account = "#{ENV['USER']}"
      target_account = self["user_account"]
      if target_account.nil?
        target_account = deploying_account
      end

      use_permabit_account = self["use_permabit_account"]
      if use_permabit_account.nil?
        use_permabit_account = false
      end

      ansible_groups = ["deploying_account = #{deploying_account}",
                        "target_account = #{target_account}",
                        "use_permabit_account = #{use_permabit_account}"]

      domain = self["domain"]
      unless domain.nil?
        ansible_groups.push("domain = #{domain}")
      end

      ansible_groups
    end
  end

  ##########################################################################
  # Default values for machine groups of a given role.
  ##########################################################################
  class RoleDefaults < ConfigHash
    self.set_converters(converters:
                          { "disks"       => "MergeableArray",
                            "user-disks"  => "Accumulator",
                            "mounts"      => "MergeableArray",
                            "user-mounts" => "Accumulator",
                          })
  end

  ##########################################################################
  # The machines.
  ##########################################################################
  class Machines < ConfigHash
    @@groups = {
      "infrastructure" => "BunsenConfig::InfrastructureMachineGroup",
      }
    @@groups.default = "BunsenConfig::MachineGroup"

    ########################################################################
    # Convert YAML to a MachineGroup of the appropriate type.
    ##
    def self.make_machine_group(value)
      Object.const_get(@@groups[value["role"]]).method(:new).call(value)
    end

    self.set_converters(default: Machines.method(:make_machine_group))

    ##########################################################################
    # @inherit
    ##
    def prepare(config)
      defaults = config["defaults"]
      self.each { |name, group|
        group["name"] = name
        role = group["role"]
        unless defaults.key?(role)
          raise "unknown role #{role} for #{name}"
        end
      }

      # Inherit any properties from other groups.
      self.values.each { |group|
        group.inherit(config)
      }

      # Strip out any groups which have no members.
      self.keep_if { |name, group|
        group["count"] > 0
      }

      # Finish preparing each group and create the list of individual machines.
      self.values.each { |group|
        group.post_merge(config)
      }

      # Enforce the requirement of 1 and only 1 infrastructure machine
      count = self.machines.select { |machine|
        machine["role"] == "infrastructure"
      }.length

      if count == 0
        raise "No infrastructure machines defined"
      end

      if count > 1
        raise "Too many infrastructure machines defined"
      end
    end

    ##########################################################################
    # Get all the machines in a list sorted by the order in which they should
    # be created.
    #
    # @return  The list of machines
    ##
    def machines()
      self.values.map(&:machines).flatten
    end

    ##########################################################################
    # @inherit
    ##
    def ansible_groups()
      if not self._prepared
        raise "Unprepared to generate ansible groups"
      end

      ansible_groups = {}
      self.machines.each { |machine|
        role = machine["role"]
        name = machine["name"]
        if not ansible_groups.key?(role)
          ansible_groups[role] = [name]
        else
          ansible_groups[role].push(name)
        end
      }

      ansible_groups
    end
  end

  ##########################################################################
  # A group of machines, i.e. a set of machines with the same role, distro,
  # and base name.
  ##########################################################################
  class MachineGroup < ConfigHash
    self.set_converters(converters:
                          { "disks"       => "MergeableArray",
                            "user-disks"  => "Accumulator",
                            "mounts"      => "MergeableArray",
                            "user-mounts" => "Accumulator",
                          })

    attr_accessor :machines

    ##########################################################################
    # Inherit parameters from a parent machine group if there is one. This must
    # be done before any of the groups are prepared so that user-<foo>s won't
    # already be merged into <foo>s. Also pick up any default parameters from
    # the role.
    #
    # @param config  The top level Config to which this group belongs.
    ##
    def inherit(config)
      # Inherit parameters from a parent group if one is specified.
      parent_name = self.delete("parent")
      if parent_name.nil?
        # If there is no parent to inherit from, pick up any defaults
        defaults = config.dig("role_defaults", self["role"])
        if defaults.nil?
          return
        end

        defaults.each { |key, value|
          if self[key].nil?
            self[key] = value
          end
        }
        return
      end

      unless config["machines"].key?(parent_name)
        raise "#{parent_name} does not exist for #{self}"
      end

      parent = config.dig("machines", parent_name)

      # Make sure the parent has done any inheriting it needs to do.
      if BunsenConfig.debug[:inherit]
        puts "#{self} inheriting from #{parent}"
      end
      parent.inherit(config)

      MachineGroup.new(parent).merge!(self).each { |key, value|
        self[key] = value
      }
    end

    ##########################################################################
    # @inherit
    ##
    def prepare(config)
      if self["memory"].nil?
        raise "'memory' not defined for #{self}"
      end
      if self["cpus"].nil?
        raise "'cpus' not defined for #{self}"
      end

      matches = self["distro"].match('([a-z]+)([0-9]+)')
      os = matches[1]
      release = matches[2]
      major = release
      minor = nil
      unless os.eql?("fedora")
        # This correctly identifies the rhel/centos major/minor pairing
        # from 7.5 (the earliest we support) to 74.x.
        split_release = release.split('')
        if (split_release[0].to_i < 7) or
           ((split_release[0].to_i == 7) and (split_release[1].to_i < 5))
          major = split_release[0..1].join("")
          minor = split_release[2..].join("")
        else
          major = split_release[0]
          minor = split_release[1..].join("")
        end
        release = "#{major}.#{minor}"
      end

      name = "#{os}-#{release}-x86_64"
      url = "http://vdo-image-store.permabit.lab.eng.bos.redhat.com/repository" +
              "/vagrant_boxes/#{name}/versions.json"
      hostvars = {}
      if os.eql?("fedora")
        hostvars["ansible_python_interpreter"] = "python3"
      elsif major.to_i >= 8
        hostvars["ansible_python_interpreter"] = "/usr/libexec/platform-python"
      end

      self["box"] = { "name"      => name,
                      "url"       => url,
                      "version"   => ">= 0",
                      "hostvars"  => hostvars }

      self["disks"].push(*self["user-disks"])
      self["mounts"].push(*self["user-mounts"]).each {
        |mount|
        mount["source"] = File.expand_path(mount["source"])
      }

      self.machines = (1 .. self["count"]).map {
        |i|
        Machine.new(self, self.hostname(config, i))
      }

      if BunsenConfig.debug[:prepared]
        if self["count"] > 0
          puts "prepared:\n#{self.inspect} "
        end
      end
    end

    ##########################################################################
    # Get the hostname for a given machine in this group.
    #
    # @param config  The config to which the machine belongs
    # @param number  The number of the host in question
    #
    # @return  The name of the host
    ##
    def hostname(config, number)
      config["environment"]["name_prefix"] + [self["name"], number].join('-')
    end

    ########################################################################
    # @inherit
    ##
    def to_s()
      self["name"]
    end
  end

  ##########################################################################
  # A MachineGroup for the infrastructure role.
  ##
  class InfrastructureMachineGroup < MachineGroup
    ##########################################################################
    # @inherit
    ##
    def hostname(config, number)
      config["environment"]["name_prefix"] + self["name"]
    end
  end

  ##########################################################################
  # An individual machine. This class is a decorator of a MachineGroup which
  # represents an individual machine in the group.
  ##
  class Machine
    # Machine needs to be Mergeable so that we can store them in other
    # Mergeables without an attempt being made to convert them to something
    # else.
    include Mergeable
    ##########################################################################
    # Initializer.
    #
    # @param group  The MachineGroup to which this machine belongs
    # @param name   The name of this machine
    ##
    def initialize(group, name)
      @group = group
      @name  = name
    end

    ##########################################################################
    # Override [] to return the value of @name if the key is 'name' and
    # otherwise to delegate lookups to the group.
    ##
    def [](key)
      (key == "name") ? @name : @group[key]
    end

    ##########################################################################
    # @inherit
    ##
    def dig(first, *rest)
      (rest.length == 0) ? self[first] : self[first].dig(*rest)
    end

    ##########################################################################
    # Get the ansible host vars for this machine.
    ##
    def ansible_host_vars()
      hostvars = self.dig("box", "hostvars")
      if hostvars.nil?
        hostvars = {}
      else
        hostvars = hostvars.clone
      end

      # The doubled JSON encoding for deploying_user_mounts is because one
      # level isn't producing sufficient quoting with version 2.0.2; it makes
      # the dictionary into an unquoted string with quoted substrings for the
      # keys and values, like:
      #
      #   ...=[{"source":"/foo","mount":"/workspace"}]
      #
      # But that parses as a string "[{source:/,mount:/workspace}]" and not a
      # dictionary, and without the internal quotes it can't be fed through
      # further JSON decoding to make a dictionary.
      hostvars["deploying_user_mounts"] = self["mounts"].to_json.to_json
      hostvars
    end
  end

  ############################################################################
  # The module entry point.
  #
  # Load and merge the possible config files.  These are, in low-to-high
  # precedence:
  # 1. the bunsen global config file (./vagrant-bunsen.yml)
  # 2. the user's bunsen config file (~user/.bunsen/vagrant-config.yml)
  # 3. the local bunsen config file (./vagrant-config.yml)
  #
  # @return The bunsen configuration
  ############################################################################
  def self.configure()
    begin
      Config.load(File.join(LOCAL_DIR, "vagrant-bunsen.yml"),
                  File.join(USER_DIR, "vagrant-config.yml"),
                  File.join(LOCAL_DIR, "vagrant-config.yml"))
    rescue => e
      puts e
      puts e.backtrace
      raise e
    end
  end
end
