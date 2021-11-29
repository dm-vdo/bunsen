require 'forwardable'
require 'singleton'

##########################################################################
# Predeclare classes needed by make_mergeable().
##
class Nothing; end
class MergeableString < String; end
class MergeableArray < Array; end
class Accumulator < MergeableArray; end
class MergeableInteger < Numeric; end
class MergeableHash < Hash; end
class MergeableBoolean; end

##########################################################################
# A module which provides support for types used in BunsenConfig merges.
##########################################################################
module Mergeable
  class << self
    attr_accessor :debug
  end

  # debug logging flags
  Mergeable.debug = {}

  ########################################################################
  # Module Methods
  ########################################################################

  ########################################################################
  # Convert a value to an appropriate Mergeable based on the type of the value.
  # This method is used as the default for MergeableHash's converters. As
  # such, it is the final fallback for any field name which does not have a
  # defined converter.
  #
  # @param value  The value to convert 
  #
  # @return the value as a Mergeable
  ##
  def self.make_mergeable(value)
    case value
    when Mergeable
      value.antialias
    when nil, Nothing
      Nothing.instance
    when Hash
      MergeableHash.new(value)
    when Array
      MergeableArray.new(value)
    when Integer
      MergeableInteger.new(value)
    when String
      MergeableString.new(value)
    when (true|false|TrueClass|FalseClass)
      MergeableBoolean.new(value)
    else
      raise "Don't know how to convert #{value}"
    end
  end

  ########################################################################
  # Mixin Methods
  ########################################################################

  ########################################################################
  # Override nil? to be true when empty. This is so that empty Mergeables
  # are not considered to exist when merging.
  #
  # @return true if the value should be ignored when merging or otherwise
  #              treated as non-existant
  ##
  def nil?()
    self.empty?
  end

  ########################################################################
  # Make a copy if necessary to avoid aliasing.
  #
  # @return An object which is safe to use when inheriting from one ConfigHash
  #         to another
  ##
  def antialias()
    self.dup()
  end

  ########################################################################
  # Default merge() method. Will return the supplied value if it is not nil.
  #
  # @param other  The prefered value to merge with the caller if it exists
  ##
  def merge(other)
    other.nil? ? self : other
  end
end

##########################################################################
# A Mergeable which is always nil but may be safely enumerated. Looking up
# a key in a ConfigHash which has not been set will generally return Nothing.
##########################################################################
class Nothing
  include Singleton
  include Mergeable
  extend Forwardable
  
  # Delegate most methods to an empty array.
  def_delegators [], :to_a, :push, :each, :map, :empty?

  ########################################################################
  # @inherit
  ##
  def antialias()  
    # Nothing is a singleton, so we can't copy it
    self
  end
  
  ########################################################################
  # Treat an undefined method as a field look up on an empty hash
  #
  # @inherit
  ##
  def method_missing(method, *args)
    key = method.to_s
    if key[-1] == '='
      raise "Erroneous attempt to assign #{key[0..-2]} on #{self}"
    end

    self
  end
end

##########################################################################
# A String which implements a merge() method.
##########################################################################
class MergeableString < String
  include Mergeable
  ########################################################################
  # Initializer.
  #
  # @param string  The initial contents of the MergeableString (will be
  #                copied); if nil, an empty string will be created
  #                
  ##
  def initialize(string="")
    super (string.nil? ? "" : string)
  end
end

##########################################################################
# An Array which implements a merge! method.  All elements of a MergeableArray
# will be converted to Mergeables.
##########################################################################
class MergeableArray < Array
  include Mergeable

  ########################################################################
  # Initializer. 
  #
  # @param value  The initial contents of the MergeableArray; if an array,
  #               it will be shallow copied; if nil, it will be converted to
  #               an empty array
  ########################################################################  
  def initialize(value=[])
    if value.nil?
      value = []
    elsif not value.kind_of?(Array)
      value = [value]
    end

    super
    self.map! { |v| Mergeable.make_mergeable(v) }
  end

  ########################################################################  
  # @inherit
  #
  # Override []= to convert values to Mergeables
  ##
  def []=(index, value)
    super(index, Mergeable.make_mergeable(value))
  end
end

##########################################################################
# A MergeableArray which implements a merge() method which appends the contents
# of the other array with those of the original.
##########################################################################
class Accumulator < MergeableArray
  ########################################################################
  # @inherit
  ##
  def merge(other)
    Accumulator.new(self).push(*other)
  end
end

##########################################################################
# An integer which implements a merge method and may exist but still be
# considered nil?.
##########################################################################
class MergeableInteger < Numeric
  include Mergeable

  ########################################################################
  # Initializer.
  #
  # @param value  The initial value
  ##
  def initialize(value = nil)
    if value.nil?
      @value = 0
    else
      @value = value.to_i
      @not_nil = true
    end
  end

  ########################################################################
  # @inherit
  ##
  def nil?()
    not @not_nil
  end

  ########################################################################
  # @inherit
  ##
  def antialias()
    # MergeableIntegers are immutable, so there's no reason to copy them
    self
  end
  
  ########################################################################
  # @inherit
  ##
  def to_s()
    @value.to_s
  end

  ########################################################################
  # @inherit
  ##
  def to_i()
    @value
  end

  ########################################################################
  # @inherit
  ##
  def coerce(other)
    [self.class.new(other.to_i), self]
  end

  ########################################################################
  # @inherit
  ##
  def <=>(other)
    to_i <=> other.to_i
  end

  ########################################################################
  # @inherit
  ##
  def ==(other)
    # It is not enough to just fall-back on <=> since we can use == to compare
    # to non-Numeric Objects.
    other.is_a?(Numeric) and ((self <=> other) == 0)
  end

  ########################################################################
  # @inherit
  ##
  def +(other)
    self.class.new(@value + other.to_i)
  end
  
  ########################################################################
  # @inherit
  ##
  def *(other)
    self.class.new(@value * other.to_i)
  end
end

##########################################################################
# Ruby has no Boolean type to base this on.
##########################################################################
class MergeableBoolean
  include Mergeable

  ########################################################################
  # Initializer.
  #
  # @param value  The initial value
  ##
  def initialize(value = nil)
    if value.nil?
      @value = false
    else
      @value = value
      @not_nil = true
    end
  end

  ########################################################################
  # @inherit
  ##
  def nil?()
    not @not_nil
  end

  ########################################################################
  # @inherit
  ##
  def to_s()
    @value.to_s
  end

  ########################################################################
  # @inherit
  ##
  def antialias()
    # MergeableBooleans are immutable, so there's no reason to copy them
    self
  end
end

##########################################################################
# An hash which converts all of its entries to Mergeables. It also claims to be
# empty (and nil) if all of its values are nil.
##########################################################################
class MergeableHash < Hash
  include Mergeable

  ########################################################################
  # Class Methods
  ########################################################################

  ########################################################################
  # Store nil into a non-existant key. This method is used as the default_proc
  # for MergeableHashes so that look ups of keys which were never defined will
  # be of the correct type as specified by the converters.
  #
  # @param hash  The hash which does not contain the key
  # @param key   The key to set to nil
  #
  # @return The converted nil
  ##
  def self.set_nil(hash, key)
    hash[key] = nil
    hash[key]
  end

  ########################################################################
  # Look up an undefined field name in the set of converters for the parent
  # class of the class doing a conversion.
  ##
  def self.inherit_converter(hash, field_name)
    hash[field_name] = @@converters.dig(self.superclass, field_name)    
  end

  ########################################################################
  # Set the converters for a MergeableHash derived class. All the parameters
  # are named and optional.
  # 
  # @oparam converters:  A hash mapping field names to converters. A converter
  #                      may be a method which takes the value to convert, or
  #                      a symbol which is the name of a class to construct
  #                      with the value to convert. Defaults to an empty hash.
  # @oparam default:     The default converter, if not nil, it will be
  #                      returned for any key not set in the converters: hash.
  # @param default_proc: A Proc which will be called for any key not set in the
  #                      converters. It will be called with two arguments, the
  #                      converters: hash, and the field name, and should
  #                      return the converter to use for the field name.
  ##
  def self.set_converters(converters:    {},
                          default:       nil,
                          default_proc: :inherit_converter)
    @@converters[self] = Hash[converters].tap {
      |hash|
      if not default.nil?
        hash.default = default
      else
        hash.default_proc = self.method(default_proc)
      end
    }
  end

  # A map from classes to the converters those classes have defined.
  @@converters = Hash.new() { |hash, key|
    # For classes which did not set any converters, just inherit converters
    # from the parent class.
    key.set_converters()
  }

  self.set_converters(default: Mergeable.method(:make_mergeable))

  ########################################################################
  # Instance Methods
  ########################################################################

  ########################################################################
  # Initializer.
  #
  # @param hash  The hash-like object being converted to a ConfigHash
  ##
  def initialize(hash = {})
    self.default_proc = MergeableHash.method(:set_nil)

    if hash.nil?
      return
    end

    hash.each do |key, value|
      if Mergeable.debug[:init]
        puts "setting #{key} to #{value}"
      end
      self[key] = value
    end
  end

  ########################################################################
  # Get the method to use for converting a value for the given key
  #
  # @param key  The key which is being set
  #
  # @return The method to use for converting the value to an appropriate type
  ##
  def get_converter(key)
    if Mergeable.debug[:get_converter]
      puts "#{self.class}.get_converter(#{key})"
    end

    converter = @@converters.dig(self.class, key)
    case converter
    when Method
      converter
    when String
      @@converters[self.class][key] = Object.const_get(converter).method(:new)
    else
      raise "Don't know how to use #{converter}, a #{converter.class} "\
            "as a converter"
    end
  end

  ########################################################################
  # Override []= to convert all values to an appropriate class before setting
  # them.
  #
  # @param key    The key to set
  # @param value  The new value of the key
  ##
  def []=(key, value)
    debug = (Mergeable.debug[:set].equal?(true) or
             (Mergeable.debug[:set] == key))
    if debug
      puts "#{self.class}[#{key}] = #{value.class}"
    end

    value = value.kind_of?(Mergeable) ?
              value.antialias :
              self.get_converter(key).call(value)
    
    if debug
      puts "converted value to type: #{value.class}"
    end
    super
  end

  ########################################################################
  # Merge another ConfigHash into this one. For each key in the other
  # ConfigHash, if that key is defined in this hash, the key's value's merge
  # method will be called on that value with the value from the other
  # hash. Otherwise, the value from the other hash will be set in this one. In
  # general, values in the other ConfigHash take precedence over values in this
  # one.
  #
  # @param other  The ConfigHash to merge with this one
  ##
  def merge!(other)
    super(other) {
      |key, old_value, new_value|
      if Mergeable.debug[:merge] == :keys
        puts "merging: #{key}"
      elsif Mergeable.debug[:merge]
        puts "merging: #{key}, old: #{old_value}, new: #{new_value}"
      end
      if old_value.kind_of?(MergeableHash)
        old_value.merge!(new_value)
      else
        old_value.merge(new_value.antialias)
      end
    }
  end
  
  ########################################################################
  # @inherit
  ##
  def antialias()
    # MergeableHashes aren't inherited, so we don't need to anti-alias them.
    self
  end
  
  ########################################################################
  # @inherit
  ##
  def empty?()
    # Consider this hash to be empty if it has no entries, or if all of its
    # entries are nil.
    super or self.values().select { |value| not value.nil? }.empty?
  end
end
