---@meta

local function use(var)
    return var
end

---Runs a command. The returned object allows to capture the exit status and the output of the program.
---@param command_line (string|Node)[] The full command line to run.
---@return Process A handle to the new process, which can be used to communicate with the process.
function Context:popen(command_line)
    use(command_line)
    return Process
end

---Allows access to the buffered output of a command.
---@class ProcessOutput
ProcessOutput = {}

---Concatenate outputs from different programs, or the standard output and standard error of a process.
---@param other ProcessOutput
---@return ProcessOutput
function ProcessOutput:__add(other)
    return other
end

---Break down the output in lines and returns an iterator to access each line.
---@return fun():string
function ProcessOutput:lines()
    return function()
        return ''
    end
end

---Allows access to a running program started by `Context.popen`
---@class Process
Process = {}

---Communicates with the running process. This command optionally sends input to stdin, then closes the input channel.
---It then waits for the program to end and returns a success flag, and the captures output and error buffers.
---@param input? string
---@return boolean, ProcessOutput, ProcessOutput
function Process:communicate(input)
    use(input)
    return true, ProcessOutput, ProcessOutput
end
