---Runs a command as a subprocess. The returned `Process` object allows capturing the exit status,
---standard output, and standard error of the subprocess.
---@param command_line (string|Node)[] The command line to execute, passed as an array of strings or `Node` objects representing file paths.
---@return Process A handle to the running process, which can be used to interact with the process and capture output.
function Context:popen(command_line)
    return Process
end

---Represents a running process that was started using `Context:popen`.
---The `Process` object enables interaction with the process, such as sending input, waiting for completion, and capturing output.
---@class (exact) Process
Process = {}

---Represents the buffered output of a process, which can include either the standard output or standard error.
---Provides methods for accessing the full output or iterating over each line.
---@class (exact) ProcessOutput
ProcessOutput = {}

---Concatenates outputs from different sources. This can be used to merge outputs from separate processes
---or to combine standard output and standard error from the same process.
---@param other ProcessOutput The other `ProcessOutput` object to concatenate.
---@return ProcessOutput A new `ProcessOutput` object containing the combined output.
---@operator add(ProcessOutput):ProcessOutput
function ProcessOutput:__add(other)
    return other
end

---Breaks down the buffered output into individual lines, returning an iterator for line-by-line access.
---This can be useful for processing the output one line at a time.
---@return fun():string An iterator function that returns each line as a string.
function ProcessOutput:lines()
    return function()
        return ''
    end
end

---Interacts with the running process by optionally sending input to its standard input,
---waiting for the process to finish, and then capturing its output and exit status.
---@param input string? Optional input to send to the process's standard input. If specified, input is sent, and the input channel is closed.
---@return boolean,ProcessOutput,ProcessOutput success A boolean indicating whether the process completed successfully (`true`) or encountered an error (`false`), and the captured standard output and error of the process as `ProcessOutput` objects.
function Process:communicate(input)
    return true, ProcessOutput, ProcessOutput
end
