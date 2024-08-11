---@meta

local function use(var)return var end

---A container for command-line options or settings. The methods `add_*` are only accessible during the `init` stage.
---@class Settings
---@field [string] EnvironmentValue
Settings = {}

---Declares a new boolean setting with optional command-line access.
---@param name string The name of the setting
---@param help string A help message that can be displayed using `--help`
---@param category? string The header to use when listing options using `--help`
---@param long? string The command-line option in its long form
---@param short? string The command-line option in its short form
---@param default_value? boolean The default value if the setting is not passed on the command line
function Settings:add_flag(
        name,
        help,
        category,
        long,
        short,
        default_value)
    use(name) use(category) use(long) use(short) use(help) use(default_value)
end

---Declares a new string setting with optional command-line access.
---@param name string The name of the setting
---@param help string A help message that can be displayed using `--help`
---@param category? string The header to use when listing options using `--help`
---@param long? string The command-line option in its long form
---@param short? string The command-line option in its short form
---@param default_value? string The default value if the setting is not passed on the command line
function Settings:add_value(
        name,
        help,
        category,
        long,
        short,
        default_value)
    use(name) use(category) use(long) use(short) use(help) use(default_value)
end

---Declares a new integer setting with optional command-line access.
---@param name string The name of the setting
---@param help string A help message that can be displayed using `--help`
---@param category? string The header to use when listing options using `--help`
---@param long? string The command-line option in its long form
---@param short? string The command-line option in its short form
---@param default_value? number The default value if the setting is not passed on the command line
function Settings:add_count(
        name,
        help,
        category,
        long,
        short,
        default_value)
    use(name) use(category) use(long) use(short) use(help) use(default_value)
end

---Declares a new list setting with optional command-line access.
---@param name string The name of the setting
---@param help string A help message that can be displayed using `--help`
---@param category? string The header to use when listing options using `--help`
---@param long? string The command-line option in its long form
---@param short? string The command-line option in its short form
---@param default_value? string[] The default value if the setting is not passed on the command line
function Settings:add_list(
        name,
        help,
        category,
        long,
        short,
        default_value)
    use(name) use(category) use(long) use(short) use(help) use(default_value)
end

---Declares a new enum setting with optional command-line access.
---@param name string The name of the setting
---@param help string A help message that can be displayed using `--help`
---@param possible_values string[] The list of values to pick from
---@param category? string The header to use when listing options using `--help`
---@param long? string The command-line option in its long form
---@param short? string The command-line option in its short form
---@param default_value? string The default value if the setting is not passed on the command line
function Settings:add_choice(
        name,
        help,
        possible_values,
        category,
        long,
        short,
        default_value)
    use(name) use(category) use(long) use(short) use(help) use(default_value) use(possible_values)
end