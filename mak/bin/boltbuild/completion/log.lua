---@meta

local function use(var)
    return var
end

---Logs a debug message. Debug messages are only printed in the console if the verbosity level is at least 2, but always
---appear in the log file.
---@param message string The message to log
function Context:debug(message)
    use(message)
end

---Logs an info message. Info messages are only printed in the console if the verbosity level is at least 1, but always
---appear in the log file.
---@param message string The message to log
function Context:info(message)
    use(message)
end

---Logs a warning message on the console and in the log file.
---@param message string The message to log
function Context:warn(message)
    use(message)
end

---Logs an error message on the console and in the log file.
---@param message string The message to log
function Context:error(message)
    use(message)
end

---Raises an error. This aborts the current call and unwinds until the previous `pcall` or `Context:try` call.
---@param message string The error message
function Context:fatal(message)
    use(message)
end

---Runs a function in a try block, logging a message before and after the code has run.
---@param message string The message to print when beginning the operation
---@param func fun():any The code to run in the try block.
function Context:try(message, func)
    use(message)
    use(func)
end
