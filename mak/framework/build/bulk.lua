---@type Context
local context = ...

local BULK_FILE_COUNT = 20
local CXX_FILE_TYPES = {
    ['cxx'] = true,
    ['cc'] = true,
    ['cpp'] = true,
    ['c++'] = true,
}

context:lua_driver('bulk',
        'magenta',
        context.path:make_node('drivers/bulk.lua'))

---@param generator Generator
---@param counter number
---@param extension string
---@return Task
local function make_bulk_task(generator, counter, extension)
    local master_node = context.bld_dir:make_node(generator.group)
    local target_node = master_node:make_node(generator.name)
    target_node = target_node:make_node('src')
    target_node = target_node:make_node(extension .. '-bulk-' .. counter .. '.' .. extension)
    table.insert(generator.source, { target_node.parent, target_node })
    return generator:declare_task('bulk', { }, { target_node })
end

---@param generator Generator
---@param source Node
---@param path Node
---@param counters number[]
---@param bulk_task_c Task|nil
---@param bulk_task_cxx Task|nil
---@return Task, Task
local function process_source(generator, source, path, counters, bulk_task_c, bulk_task_cxx)
    local source_type = source:extension()
    if source_type == 'c' then
        if not bulk_task_c or #bulk_task_c.env.FILES >= BULK_FILE_COUNT then
            local counter = counters[1]
            counters[1] = counter + 1
            bulk_task_c = make_bulk_task(generator, counter, 'c')
        end
        bulk_task_c.env:append('FILES', source)
    elseif CXX_FILE_TYPES[source_type] then
        if not bulk_task_cxx or #bulk_task_cxx.env.FILES >= BULK_FILE_COUNT then
            local counter = counters[2]
            counters[2] = counter + 1
            bulk_task_cxx = make_bulk_task(generator, counter, 'cc')
        end
        bulk_task_cxx.env:append('FILES', source)
    else
        table.insert(generator.source, { path, source })
    end

    return bulk_task_c, bulk_task_cxx
end

---@param generator Generator
context:feature('c,cxx', 'generate_bulk', function(generator)
    if context.settings.nobulk then
        return
    end
    if generator:has_property('nobulk') then
        return
    end

    local sources = generator.source
    generator.source = { }
    local bulk_file_c
    local bulk_file_cxx
    local indices = { 0, 0 }
    for _, source_spec in ipairs(generator.source_patterns) do
        local path = source_spec[1]
        local pattern = source_spec[2]
        for _, source_node in ipairs(context:search(path, pattern)) do
            if generator.source_filter(source_node, path, generator.env) then
                bulk_file_c, bulk_file_cxx = process_source(generator, source_node, path, indices, bulk_file_c, bulk_file_cxx)
            end
        end
    end
    generator.source_patterns = { }
    for _, source_spec in ipairs(sources) do
        local path = source_spec[1]
        local source_node = source_spec[2]
        if generator.source_filter(source_node, path, generator.env) then
            bulk_file_c, bulk_file_cxx = process_source(generator, source_node, path, indices, bulk_file_c, bulk_file_cxx)
        end
    end
end)   :set_run_after({ 'process_out_source' })
       :set_run_before({ 'process_source' })
