require 'yaml'
require 'yaml/store'

class VirtualBox
  DEFAULT_NETWORK = "172.28.128"
  INFO_FILE_NAME  = ".virtualbox.info"
  IP_DATABASE     = "vagrant.virtualbox.ip.yml"

  ########################################################################
  # Initializer.
  ##
  def initialize(info_dir, ip_dir)
    @info_dir    = info_dir
    @ip_dir      = ip_dir
    @info_file   = File.join(@info_dir, VirtualBox::INFO_FILE_NAME)
    @ip_database = File.join(@ip_dir, VirtualBox::IP_DATABASE)
  end

  ##########################################################################  
  # Get the identifier and ip address for a virtual box instance, creating
  # the id and assigning the address if necessary.
  #
  # @param name     The name of the instance
  # @param network  The network address from which to assign the address if
  #                 necessary; defaults to 172.28.128.
  # 
  # @return The instance info
  ##
  def get_info(name, network=DEFAULT_NETWORK)
    transaction {
      value = @info[name]
      if not value
        value = @info[name] = {
          'id' => make_id(),
          'ip' => assign_address(network),
        }
      end

      value
    }
  end

  ##########################################################################
  # Delete the information for an instance
  #
  # @param name  The name of the instance
  ##
  def delete_info(name)
    raise "Unimplemented"
  end

  private

  ##########################################################################
  # Generate a new instance id.
  #
  # @return The id
  ##
  def make_id()
    `hexdump -n 16 -v -e '/1 "%02X"' /dev/urandom`
  end

  ##########################################################################
  # Assign an IP address
  #
  # @param network  The network on which to assign the address
  #
  # @return The newly assigned address
  #
  # @throws If there are no addresses available on the specified network
  ##
  def assign_address(network)
    puts "assiging address for #{network}"
    subnet = ip_transaction { 
      if @ips.root?(network)
        @ips[network]
      else 
        @ips[network] = { 'assigned'     => [],
                          'network-bits' => 24,
                        }
      end
    }

    addresses = ((32 - subnet['network-bits']) ** 2) - 2
    if subnet['assigned'].length >= addresses
      raise "Can't assign address in #{network}, all are taken"
    end

    assigned = subnet['assigned'].sort
    ip = 1
    while assigned.length > 0
      if assigned.shift != ip
        break
      end
      
      ip = ip + 1
    end

    ip_transaction { @ips[network]['assigned'].push(ip) }
    return "#{network}.#{ip}"
  end

  ##########################################################################
  # Import instance info from an old style .virtualbox.<name>.info file. Once
  # imported, the old info file will be deleted.
  #
  # @param name  The name of the instance
  ##
  def import(name)
    # Import the old info file if there is one
    file = File.join(@info_dir, ".virtualbox.#{name}.info")
    if not File.exist?(file)
      return
    end
    
    info = YAML.load_file(file)
    transaction {
      if not @info.key?(name)
        @info[name] = info
      end
    }
    File.delete(file)
  end

  ##########################################################################
  # Perform a transaction on the info store, loading and/or creating the
  # store if necessary.
  #
  # @param &block  The block to execute transactionally on the store
  #
  # @return the output of the block
  ##
  def transaction(&block)
    @info ||= YAML::Store.new(@info_file)
    @info.transaction(&block)
  end
  
  ##########################################################################
  # Perform a transaction on the ip database, loading and/or creating it if
  # necessary. If there is an old ip database, it will imported and removed.
  #
  # @param &block  The block to execute transactionally on the store
  #
  # @return the output of the block
  ##
  def ip_transaction(&block)
    load_ips().transaction(&block)
  end
  
  ##########################################################################
  # Load the ip database if it hasn't already been. If there is an old
  # database, import and delete it.
  #
  # @return The loaded database
  ##
  def load_ips()
    if @ips
      return @ips
    end
    
    @ips = YAML::Store.new(@ip_database)
    
    # Convert old file if it exists
    file = File.join(@ip_dir, "vagrant.virtualbox.ip")
    if not File.exist?(file)
      return @ips
    end
    
    ips = YAML.load_file(file)
    ips['ips'][0] = false
    ips['ips'][255] = false        
    address_range = 0..ips['ips'].length - 1
    @ips.transaction { 
      @ips[ips['subnet']] = {
        'assigned'       => address_range.select { |ip| ips['ips'][ip] },
        'network-bits'   => 24,
      }
    }
    File.delete(file)
    
    return @ips
  end
end
