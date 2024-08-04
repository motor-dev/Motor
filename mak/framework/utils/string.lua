function string:starts_with(start)
    return self:sub(1, #start) == start
end

function string:trim()
    return self:match("^%s*(.-)%s*$")
end

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
