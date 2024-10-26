---@type(Context)
local context = ...

context:load_tool('clang')
for _, env in ipairs(Clang.discover({ '--std', 'c++20' })) do

end
