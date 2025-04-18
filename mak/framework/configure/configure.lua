---@type Context
local context = ...

context:recurse('metagen.lua')

Bolt.Flex.find_flex()
Bolt.Bison.find_bison()
Bolt.Wget.find_wget()

Motor = {
    compilers = {}
}

function Motor.add_compiler(env)
    table.insert(Motor.compilers, env)
end

function Motor.test_compiler(env, code)
    local src = context.bld_dir:make_node('main.cc')
    local target = context.bld_dir:make_node('out')
    local command = {}
    src:write(code)
    for _, arg in ipairs(env.CXX) do
        table.insert(command, arg)
    end
    for _, arg in ipairs(env.CXXFLAGS) do
        table.insert(command, arg)
    end
    table.insert(command, src:abs_path())
    -- TODO: properly parse the output flag
    table.insert(command, '-o')
    table.insert(command, target:abs_path())

    local result = pcall(function()
        return context:popen(command):communicate()
    end)

    src:try_delete()
    target:try_delete()

    return result
end

function Motor.create_toolchain(env)
    local target_name = env.TOOLCHAIN_ID
    local setup = context:declare_command('setup:' .. target_name, 'setup', env)
    ---@type string[]
    local flavors = context.settings.flavors
    for _, flavor in ipairs(flavors) do
        context:chain_command(setup, 'build:' .. target_name .. ':' .. flavor, 'build')
    end
    if context.env.WITH_ASAN ~= nil then
        context:chain_command(setup, 'build:' .. target_name .. ':asan', 'build')
    end
    if context.env.WITH_TSAN ~= nil then
        context:chain_command(setup, 'build:' .. target_name .. ':tsan', 'build')
    end
    if context.env.WITH_UBSAN ~= nil then
        context:chain_command(setup, 'build:' .. target_name .. ':ubsan', 'build')
    end
end

context:recurse('host/' .. context.settings.OS .. '.lua')

local compilers = {}
local platforms = {}
for _, c in ipairs(context:search(context.path, 'compiler/*.lua')) do
    table.insert(compilers, c:basename())
end
for _, p in ipairs(context:search(context.path, 'target/*.lua')) do
    table.insert(platforms, p:basename())
end

compilers = context.settings.compiler or compilers
platforms = context.settings.platform or platforms

---@cast compilers string[]
---@cast platforms string[]

for _, compiler in ipairs(compilers) do
    context:recurse('compiler/' .. compiler .. '.lua')
end

table.sort(Motor.compilers, function(env1, env2)
    return env1.TOOLCHAIN_ID < env2.TOOLCHAIN_ID
end)
for _, platform in ipairs(platforms) do
    context:recurse('target/' .. platform .. '.lua')
end

local env = context:derive()
env.PROJECTS = true
env.TOOLCHAIN_ID = 'IDEs'
local setup = context:declare_command("setup:projects", "setup", env)
context:chain_command(setup, "clion", "build")
context:chain_command(setup, "vs2017", "build")
context:chain_command(setup, "vs2019", "build")
context:chain_command(setup, "vs2022", "build")
context:chain_command(setup, "visual_studio:cmake", "build")
context:chain_command(setup, "vscode", "build")
context:chain_command(setup, "vscode:cpp", "build")
context:chain_command(setup, "vscode:cmake", "build")
context:chain_command(setup, "qtcreator", "build")
context:chain_command(setup, "qtcreator:qbs", "build")
context:chain_command(setup, "qtcreator:cmake", "build")
context:chain_command(setup, "xcode", "build")
