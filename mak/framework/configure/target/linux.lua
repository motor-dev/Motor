---@type Context
local context = ...

for _, compiler in ipairs(--[[---@type Compiler[] ]] context.compilers) do
    if compiler.target:find('%-linux%-gnu') then
        if pcall(function()
            local node = context.bld_dir:make_node('a.out')
            local r, out, err = compiler:run_cxx({ '-o', node:abs_path(), '-' }, "#include <cstdio>\n#include <cfloat>\n#include <new>\nint main() {}\n")
            node:try_delete()
            if not r then
                error()
            end
        end) then
            context:create_toolchain(compiler, context.Platform:new {
                name = "linux",
                setup = function(c)
                    context.env.PROGRAM_PATTERN = '%s'
                    context.env.SHLIB_PATTERN = 'lib%s.so'
                    context.env.STLIB_PATTERN = 'lib%s.a'
                end
            })
        end
    end
end