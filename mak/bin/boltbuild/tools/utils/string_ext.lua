---Checks if the string begins with the specified prefix.
---@param prefix string The prefix to check against the beginning of the string.
---@return boolean true if the string starts with the specified prefix, otherwise false.
function string:starts_with(prefix)
    return self:sub(1, #prefix) == prefix
end

---Removes whitespace from the beginning and end of the string.
---@return string The original string, trimmed of leading and trailing whitespace.
function string:trim()
    return --[[---@type string]] self:match("^%s*(.-)%s*$")
end

---Splits the string into an array of substrings based on a specified separator.
---@param sep string|nil An optional separator to use to split the string. Defaults to whitespace if not provided.
---@return string[] An array of components split by the separator.
function string:split(sep)
    if sep == nil then
        sep = "%s"
    end
    local t = {}
    for str in self:gmatch("([^" .. sep .. "]+)") do
        table.insert(t, str)
    end
    return t
end

---Concatenates elements of a list into a single string, separated by the specified separator.
---@param separator string The separator to insert between each element.
---@param iterable string[] The list of strings to join into a single string.
---@return string The concatenated string with elements joined by the separator.
function string.join(separator, iterable)
    local count = #iterable
    local result = ''
    for i, s in ipairs(iterable) do
        result = result .. s
        if i ~= count then
            result = result .. separator
        end
    end
    return result
end