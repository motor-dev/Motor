---@meta

local function use(var)
    return var
end

---Search for files on the filesystem. Using `directory` as a starting point, returns all files (as `Node` objects) that
---match the given pattern. Search results returned by this function are stored and will be used to check if a context is
---up-to-date in a subsequent run of the tool.
---@param directory Node The root directory of the search
---@param pattern string A glob pattern
---@param include_directories boolean? Wether directories are returned
---@return Node[] A list of nodes that matched the pattern.
function Context:search(directory, pattern, include_directories)
    use(directory)
    use(pattern)
    use(include_directories)
    return {}
end

---Represents a filesystem object, either a directory or a file, that potentially does not exist yet.
---@class Node
---@field parent Node
local Node

---Returns the last component of the path of the filesystem object, i.e. the directory or file name
---@return string The last component of the path, which represents the directory or file name.
function Node:name()
    return ''
end

---Returns the complete path of the filesystem object
---@return string The absolute path
function Node:abs_path()
    return ''
end

---Creates a new Node object representing a filesystem object, either relative to `self` or absolute.
---@param path string A path, absolute or relative to self.
---@return Node A node representing the path given as argument.
function Node:make_node(path)
    use(path)
    return Node
end

---Checks if the filesystem object exists and is a directory.
---@return boolean true if the node represents an existing directory.
function Node:is_dir()
    return false
end

---Checks if the filesystem object exists and is a file object.
---@return boolean true if the node represents an existing file.
function Node:is_file()
    return false
end

---Creates a directory.
function Node:mkdir()
end

---Deletes a file on disk. Raises an error if the operation cannot be completed.
function Node:delete()
end

---Deletes a file on disk. Ignores any error.
function Node:try_delete()
end

