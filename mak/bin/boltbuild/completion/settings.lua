---@meta

---A container for managing command-line options or general settings for a program.
---Settings allow values to be configured via command-line arguments, and each setting type can be declared with methods prefixed by `add_*`.
---These `add_*` methods are only available during the `init` stage of the tool's lifecycle.
---@class Settings
---@field [string] EnvironmentValue Holds environment values mapped to string keys, for storing any program-defined settings.
Settings = {}

---Represents a command-line option that has been declared within `Settings`.
---The option may be of various types, such as a boolean flag, string, integer count, list, or an enumerated choice.
---@class CommandLineOption
CommandLineOption = {}

---Declares a new boolean setting, representing a flag that can be toggled on or off.
---This setting can optionally be configured from the command line.
---@param name string The name of the setting, used as a key for retrieval.
---@param help string A help message displayed in the `--help` output, describing the setting's purpose.
---@param default_value boolean? The default value of the flag if it is not specified on the command line; defaults to `false` if unspecified.
---@return CommandLineOption #A `CommandLineOption` object for further configuration.
function Settings:add_flag(name, help, default_value)
end

---Declares a new string setting, allowing users to input arbitrary text values.
---@param name string The name of the setting, used as a key for retrieval.
---@param help string A help message displayed in the `--help` output, describing the setting's purpose.
---@param default_value string? The default value if the setting is not specified on the command line.
---@return CommandLineOption #A `CommandLineOption` object for further configuration.
function Settings:add_value(name, help, default_value)
end

---Declares a new integer setting, often used for counters or specifying numerical values.
---@param name string The name of the setting, used as a key for retrieval.
---@param help string A help message displayed in the `--help` output, describing the setting's purpose.
---@param default_value number? The default value if the setting is not specified on the command line.
---@return CommandLineOption #A `CommandLineOption` object for further configuration.
function Settings:add_count(name, help, default_value)
end

---Declares a new list setting, allowing multiple values to be provided as a comma-separated list.
---@param name string The name of the setting, used as a key for retrieval.
---@param help string A help message displayed in the `--help` output, describing the setting's purpose.
---@param default_value string[]? The default list of values if none are provided on the command line.
---@return CommandLineOption #A `CommandLineOption` object for further configuration.
function Settings:add_list(name, help, default_value)
end

---Declares a new enum setting, restricting input to a defined set of valid string values.
---@param name string The name of the setting, used as a key for retrieval.
---@param help string A help message displayed in the `--help` output, describing the setting's purpose.
---@param possible_values string[] An array of valid values that this setting can accept.
---@param default_value string? The default value if the setting is not specified on the command line.
---@return CommandLineOption #A `CommandLineOption` object for further configuration.
function Settings:add_choice(name, help, possible_values, default_value)
end

---Specifies a category for the command-line option, helping to organize options within `--help` output.
---@param category string The category name under which this option will appear in help documentation.
---@return CommandLineOption #The current `CommandLineOption` object, allowing method chaining.
function CommandLineOption:set_category(category)
end

---Sets the full (long) form of the option as it will appear on the command line.
---For example, setting `--verbose` as the long form of a flag.
---@param long string The long version of the option (e.g., `--verbose`).
---@return CommandLineOption #The current `CommandLineOption` object, allowing method chaining.
function CommandLineOption:set_long(long)
end

---Sets the abbreviated (short) form of the option as it will appear on the command line.
---For example, setting `-v` as the short form of a flag.
---@param short string The short version of the option (e.g., `-v`).
---@return CommandLineOption #The current `CommandLineOption` object, allowing method chaining.
function CommandLineOption:set_short(short)
end

---Marks this option as required, meaning that the program will enforce that it is specified at runtime.
---If omitted, the program will produce an error indicating the option must be provided.
---@return CommandLineOption #The current `CommandLineOption` object, allowing method chaining.
function CommandLineOption:set_required()
end
