---@meta

local function use(var)return var end

---Represents a filesystem object, either a directory or a file, that potentially does not exist yet.
---@class Node
---@field parent Node
local Node

---Returns the last component of the path of the filesystem object, i.e. the directory or file name
---@return string The last component of the path, which represents the directory or file name.
function Node:name() return '' end

---Returns the complete path of the filesystem object
---@return string The absolute path
function Node:abs_path() return '' end

---Creates a new Node object representing a filesystem object, either relative to `self` or absolute.
---@param path string A path, absolute or relative to self.
---@return Node A node representing the path given as argument.
function Node:make_node(path)use(path) return Node end

---Checks if the filesystem object exists and is a directory.
---@return boolean true if the node represents an existing directory.
function Node:is_dir() return false end

---Checks if the filesystem object exists and is a file object.
---@return boolean true if the node represents an existing file.
function Node:is_file() return false end
