local context = ...
context:try('setting up environment', function()
    return context.env.TOOLCHAIN_ID
end)

if not context.env.PROJECTS then
    local target_name = context.env.TOOLCHAIN_ID
    ---@type string[]
    local flavors = context.settings.flavors
    for _, flavor in ipairs(flavors) do
        context:declare_command('build:' .. target_name .. ':' .. flavor, 'build', context.env)
    end
else
    context:declare_command("clion", "build")
    context:declare_command("vs2017", "build")
    context:declare_command("vs2019", "build")
    context:declare_command("vs2022", "build")
    context:declare_command("vscode", "build")
    context:declare_command("vscode_cmake", "build")
    context:declare_command("qtcreator", "build")
    context:declare_command("qtcreator_qbs", "build")
    context:declare_command("xcode", "build")
end
