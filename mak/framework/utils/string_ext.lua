---@param prefix string The prefix to check
---@return boolean true if the string starts with the specified prefix
function string:starts_with(prefix)
    return self:sub(1, #prefix) == prefix
end

---@return string The original string, trimmed of starting and ending blanks
function string:trim()
    return --[[---@type string]] self:match("^%s*(.-)%s*$")
end

---@param sep? string An optional separator to use to break the string
---@return string[] An array of components
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

---Creates a string by concatenating the elements in an iterable, separated by the given separator.
---@param separator string The separator to use between elements.
---@param iterable string[] The list of strings to join.
---@return string The concatenated string.
function string.join(separator, iterable)
    local count = #iterable
    local result = ''
    for i, s in ipairs(iterable) do
        result = result..s
        if i ~= count then
            result = result .. separator
        end
    end
    return result
end
