context = ...

for _, tool in ipairs(context.compilers) do
    tool, compiler, architecture, target = table.unpack(tool)
    if target:find('%-linux%-gnu') then
        context:with(context:derive(context.env), function()
        end)
    end
end