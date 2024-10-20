---@meta

local function use(var)return var end

---A container for command-line options or settings. The methods `add_*` are only accessible during the `init` stage.
---@class Settings
---@field [string] EnvironmentValue
Settings = {}

---A command-line option.
---@class CommandLineOption
CommandLineOption = {}

---Declares a new boolean setting with optional command-line access.
---@param name string The name of the setting
---@param help string A help message that can be displayed using `--help`
---@param default_value? boolean The default value if the setting is not passed on the command line
---@return CommandLineOption the new option, for further editing.
function Settings:add_flag(
        name,
        help,
        default_value)
    use(name) use(help) use(default_value)
end

---Declares a new string setting with optional command-line access.
---@param name string The name of the setting
---@param help string A help message that can be displayed using `--help`
---@param default_value? string The default value if the setting is not passed on the command line
---@return CommandLineOption the new option, for further editing.
function Settings:add_value(
        name,
        help,
        default_value)
    use(name) use(help) use(default_value)
end

---Declares a new integer setting with optional command-line access.
---@param name string The name of the setting
---@param help string A help message that can be displayed using `--help`
---@param default_value? number The default value if the setting is not passed on the command line
---@return CommandLineOption the new option, for further editing.
function Settings:add_count(
        name,
        help,
        default_value)
    use(name) use(help) use(default_value)
end

---Declares a new list setting with optional command-line access.
---@param name string The name of the setting
---@param help string A help message that can be displayed using `--help`
---@param default_value? string[] The default value if the setting is not passed on the command line
---@return CommandLineOption the new option, for further editing.
function Settings:add_list(
        name,
        help,
        default_value)
    use(name) use(help) use(default_value)
end

---Declares a new enum setting with optional command-line access.
---@param name string The name of the setting
---@param help string A help message that can be displayed using `--help`
---@param possible_values string[] The list of values to pick from
---@param default_value? string The default value if the setting is not passed on the command line
---@return CommandLineOption the new option, for further editing.
function Settings:add_choice(
        name,
        help,
        possible_values,
        default_value)
    use(name) use(help) use(default_value) use(possible_values)
end


---Sets the category of the option. This helps sorting options in the help menu.
---@param category string The header to use when listing options using `--help`
---@return CommandLineOption the same option, for further editing.
function CommandLineOption:set_category(category)
    use(category)
end

---Sets the long version of the flag on the command line.
---@param long string The command-line option in its long form
---@return CommandLineOption the same option, for further editing.
function CommandLineOption:set_long(long)
    use(long)
end

---Sets the short version of the flag on the command line.
---@param short string The command-line option in its short form
---@return CommandLineOption the same option, for further editing.
function CommandLineOption:set_short(short)
    use(short)
end

---Makes the option a required option.
---@return CommandLineOption the same option, for further editing.
function CommandLineOption:set_required()

end
