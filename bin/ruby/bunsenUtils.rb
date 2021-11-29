##########################################################################
# This module contains miscellaneous utilities used by the Bunsen Vagrantfile
##
module BunsenUtils
  ##########################################################################
  # Check wether a vagrant plugin is installed.
  #
  # @param plugin  The name of the plugin to check
  #
  # @throws if the specified plugin is not installed
  ##
  def self.assert_plugin_exists(plugin)
    unless Vagrant.has_plugin?(plugin)
    raise "#{plugin} is not installed. Please install it by running \
           'vagrant plugin install #{plugin}'"
    end
  end
end


