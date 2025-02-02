---@type Context
local context = ...

find_wsl_path = function(path)
    local paths = {}
    local command = { 'wsl.exe', '-l', '-q' }
    local result, out, err = context:popen(command):communicate()
    if result then
        for dist in out:lines() do
            dist = dist:trim()
            if dist:len() > 0 then
                local command = { 'wsl.exe', '-d', dist, 'echo', '$PATH' }
                local result, out, err = context:popen(command):communicate()
                if result then
                    for path in out:lines() do
                        path = path:split(':')
                        for _, p in ipairs(path) do
                            if not string.starts_with(p, '/mnt/') then
                                table.insert(paths, '\\\\wsl$\\' .. dist .. p:gsub('/', '\\'))
                            end
                        end
                    end

                    for _, p in ipairs(paths) do
                        print(p)
                    end
                else
                    print(result, err)
                end
            end
        end
    else
        print(result, err)
    end
end

context:try('Looking for wsl', find_wsl_path)
