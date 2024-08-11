---@meta

local function use(var)return var end

---Allows access to the buffered output of a command.
---@class ProcessOutput
ProcessOutput = {}

---Concatenate outputs from different programs, or the standard output and standard error of a process.
---@param other ProcessOutput
---@return ProcessOutput
function ProcessOutput:__add(other) return other end

---Break down the output in lines and returns an iterator to access each line.
---@return fun():string
function ProcessOutput:lines() return function()return '' end end

---Allows access to a running program started by `Context.popen`
---@class Process
Process = {}


---Communicates with the running process. This command optionally sends input to stdin, then closes the input channel.
---It then waits for the program to end and returns a success flag, and the captures output and error buffers.
---@param input? string
---@return boolean, ProcessOutput, ProcessOutput
function Process:communicate(input)use(input) return true, ProcessOutput, ProcessOutput end
