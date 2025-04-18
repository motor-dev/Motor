---@type Context
local context = ...
context:load_tool('internal/bolt')

Bolt.PkgConfig = {}

---@return string[]
---@return string[]
---@return string[]
local function _run_pkg_config(pkg_name, lib_paths, seen)
    if seen[pkg_name] then
        return {}, {}, {}
    end
    seen[pkg_name] = true

    local expand = {}
    local configs = {}

    local config_file
    for _, p in ipairs(lib_paths) do
        local node = p:make_node('pkgconfig/' .. pkg_name .. '.pc')
        if node:is_file() then
            config_file = node
            break
        end
    end

    if not config_file or not config_file:is_file() then
        context:raise_error('no pkg-config file for library ' .. pkg_name)
    end
    ---@cast config_file -nil

    local file = io.open(config_file:abs_path(), 'r')
    if not file then
        context:raise_error('no pkg-config file for library ' .. pkg_name)
    end
    ---@cast file -nil

    local lines = file:lines()
    for line in lines do
        ---@cast line string
        line = line:match('^%s*(.-)%s*$')
        if line == '' or line:sub(1, 1) == '#' then
            goto continue
        end

        local pos = line:find('=')
        local pos2 = line:find(':')
        if pos and (not pos2 or pos2 > pos) then
            local var_name = line:sub(1, pos - 1):match('^%s*(.-)%s*$')
            local value = line:sub(pos + 1):match('^%s*(.-)%s*$')
            if value:sub(1, 1) == '"' and value:sub(-1) == '"' then
                value = value:sub(2, -2)
            end
            --if sysroot ~= '' and value:sub(1, 1) == '/' then
            --    value = sysroot .. value:sub(2)
            --end
            value = value:gsub('%${(%w+)}', function(name)
                return expand[name] or ''
            end)
            expand[var_name] = value
            goto continue
        end

        pos = line:find(':')
        if pos then
            local var_name = line:sub(1, pos - 1):match('^%s*(.-)%s*$')
            local value = line:sub(pos + 1):match('^%s*(.-)%s*$')
            value = value:gsub('%${(%w+)}', function(name)
                return expand[name] or ''
            end)
            configs[var_name] = {}
            for v in value:gmatch('[^%s]+') do
                table.insert(configs[var_name], v)
            end
        end

        :: continue ::
    end
    file:close()

    local cflags, libs, ldflags = {}, {}, {}
    local skip = false
    for _, d in ipairs(configs.Requires or {}) do
        if skip then
            skip = false
        elseif d == '=' or d == '<' or d == '<=' or d == '>' or d == '>=' then
            skip = true
        else
            local dep_c_flags, dep_libs, dep_ld_flags
            if not seen[d] then
                dep_c_flags, dep_libs, dep_ld_flags = Bolt.PkgConfig.run_pkg_config(d)
                for _, v in ipairs(dep_c_flags) do
                    table.insert(cflags, v)
                end
                for _, v in ipairs(dep_libs) do
                    table.insert(libs, v)
                end
                for _, v in ipairs(dep_ld_flags) do
                    table.insert(ldflags, v)
                end
            end
        end
    end

    for _, f in ipairs(configs.Cflags or {}) do
        if f:sub(1, 2) == '-I' then
            local include = f:sub(3)
            --if include:sub(1, 1) == '/' and not include:find(sysroot, 1, true) then
            --    include = sysroot .. include:sub(2)
            --end
            table.insert(cflags, context.env.C_IDIRAFTER .. include)
        else
            table.insert(cflags, f)
        end
    end

    for _, f in ipairs(configs.Libs or {}) do
        if f:sub(1, 2) == '-l' then
            table.insert(libs, f:sub(3))
        elseif f:sub(1, 2) == '-L' then
            local libdir = f:sub(3)
            --if libdir:sub(1, 1) == '/' and not libdir:find(sysroot, 1, true) then
            --    libdir = sysroot .. libdir
            --end
            table.insert(ldflags, context.env.LINK_LIBPATH_F .. libdir)
        else
            table.insert(ldflags, f)
        end
    end

    return cflags, libs, ldflags
end

---@param pkg_name string The name of the package to query.
---@return string[] #The compiler flags for the package.
---@return string[] #The libraries for the package.
---@return string[] #The linker flags for the package.
function Bolt.PkgConfig.run_pkg_config(pkg_name)
    local lib_paths = context.env.C_COMPILER_SYSTEM_LIB_DIRS or {}

    --for _, t in ipairs(context.env.TARGETS or {}) do
    --    table.insert(lib_paths, '=/usr/lib/' .. t)
    --    table.insert(lib_paths, '=/usr/libdata/' .. t)
    --end

    --for i, path in ipairs(lib_paths) do
    --    lib_paths[i] = extend_path(path, sysroot)
    --end

    local seen = {}

    return _run_pkg_config(pkg_name, lib_paths, seen)
end

function Bolt.PkgConfig.pkg_config(name, var)
    local cflags, libs, ldflags = Bolt.PkgConfig.run_pkg_config(name)
    context.env['check_' .. var] = true
    context.env['check_' .. var .. '_cflags'] = cflags
    context.env['check_' .. var .. '_cxxflags'] = cflags
    context.env['check_' .. var .. '_libs'] = libs
    context.env['check_' .. var .. '_ldflags'] = ldflags
end
