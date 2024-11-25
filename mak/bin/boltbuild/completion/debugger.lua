---@meta
local function use(var)
    return var
end

--- Starts a debug server.
--- This function initializes and starts a debug server at the specified address and port.
---
--- @param address string|nil The address to bind the debug server to. Defaults to 127.0.0.1 if unspecified.
--- @param port number|nil The port to bind the debug server to.
function Context:start_debug_server(address, port)
    use(address)
    use(port)
end

--- Connects to a debugger.
--- This function connects to a debugger at the specified address and port.
---
--- @param address string|nil The address of the debugger to connect to. Defaults to 127.0.0.1 if unspecified.
--- @param port number The port of the debugger to connect to. Defaults to 9966 if unspecified.
function Context:connect_to_debugger(address, port)
    use(address)
    use(port)
end
