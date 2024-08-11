---@param prefix string The prefix to check
---@return boolean true if the string starts with the specified prefix
function string:starts_with(prefix)
    return self:sub(1, #prefix) == prefix
end

---@return string The original string, trimmed of starting and ending blanks
function string:trim()
    return --[[---@type string]] self:match("^%s*(.-)%s*$")
end

---@param sep string|nil An optional separator to use to break the string
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
