--- Logs a debug-level message.
--- Debug messages provide detailed information for troubleshooting and are shown in the console only if the verbosity
--- level is set to 2 or higher, but they are always recorded in the log file.
---@param message string The debug message to log.
function Context:debug(message)
end

--- Logs an informational message.
--- Info messages provide general updates and are shown in the console if the verbosity level is at least 1.
--- They are always recorded in the log file, regardless of verbosity level.
---@param message string The informational message to log.
function Context:info(message)
end

--- Logs a warning message.
--- Warnings indicate potential issues or non-critical errors. They are shown on the console and recorded in the log file.
---@param message string The warning message to log.
function Context:warn(message)
end

--- Logs an error message.
--- Error messages indicate critical issues in execution. They are displayed on the console and recorded in the log file.
---@param message string The error message to log.
function Context:error(message)
end

--- Raises a critical error, logging a message and generating a Lua error.
--- This function is typically used to signal a severe issue, logging the error message and raising a Lua error that can
--- still be caught by the caller if using `pcall` or a similar mechanism. This does not force termination, but indicates
--- a condition that should ideally stop normal operation unless handled by the caller.
---
---@param message string The error message to log and raise.
function Context:raise_error(message)
end

--- Prints a plain message to the console.
--- This message is only output to the console and not logged to the log file.
---@param message string The message to print.
function Context:print(message)
end

--- Prints a formatted message to the console, with support for text and background colors.
--- If the terminal supports ANSI colors, any valid color name enclosed in braces can format the message.
--- - For text colors, use `{red}`, `{blue}`, `{green}`, `{dark_red}`, `{dark_green}`, etc.
--- - For background colors, use `{bg:red}`, `{bg:blue}`, `{bg:dark_red}`, etc.
--- - Supported colors include ANSI color names like `red`, `purple`, `white`, as well as `dark_red`, `dark_green`, etc.
--- - Use `{reset}` to reset text color and `{bg:reset}` to reset the background color to default.
---
---@param message string The message to print, with optional color and background formatting.
function Context:color_print(message)
end

--- Runs a function within a "try" block, logging messages before and after execution, and returning a boolean indicating success.
--- - Logs `message` before starting the operation.
--- - Most terminal logging is disabled inside a `try` block (including nested `try` blocks), except for messages directly
---   related to the `try` operation itself.
--- - If the function executes without errors:
---     - Logs the function’s return value in green if it provides one.
---     - Logs `"ok"` if the function returns `nil`, indicating successful completion.
---     - Returns `true` to signal success.
--- - If the function raises an error:
---     - Captures and logs the error message in yellow as an exit message.
---     - Returns `false` to indicate failure.
---
---@param message string The message to log before the operation begins.
---@param func fun():any The function to run within the try block.
---@return boolean true if the function completed successfully; `false` if an error occurred.
function Context:try(message, func)
end
