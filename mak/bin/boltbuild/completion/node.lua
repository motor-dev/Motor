---@meta

local function use(var)
    return var
end

--- Search for files on the filesystem. Using `directory` as a starting point, returns all files (as `Node` objects) that
--- match the given pattern. Search results returned by this function are verified again on every run, and the command will
--- be reevaluated if the search results change.
---
---@param directory Node The root directory of the search
---@param pattern string A glob pattern
---@param include_directories boolean|nil Optional. Wether directories are returned
---@return Node[] A list of nodes that matched the pattern.
function Context:search(directory, pattern, include_directories)
    use(directory)
    use(pattern)
    use(include_directories)
    return {}
end

--- Finds a program by name within the specified paths.
--- This function searches for an executable program with the given `name` in the provided `paths`.
--- If `paths` is not provided, the `context.options.path` variable will be used, which defaults to the environment PATH variable.
--- Search results returned by this function are verified again on every run, and the command will
--- be reevaluated if the search results change.
---
---@param name string The name of the program to find.
---@param paths string[]|nil Optional. A list of paths to search for the program. If not specified, the `context.options.path` variable is used.
---@return Node The node representing the found program.
function Context:find_program(name, paths)
    use(name)
    use(paths)
    return Node
end

--- Represents a filesystem object, either a directory or a file, which may or may not exist yet.
--- Nodes serve as filesystem object references that can represent either directories or files, providing a range of utilities for path manipulation and file operations.
---@class Node
---@field parent Node The parent node of this node, representing the directory containing this filesystem object.
local Node

--- Creates a new Node object representing a filesystem object, either relative to `self` or absolute.
---@param path string A filesystem path, either absolute or relative to `self`.
---@return Node A new Node representing the specified path.
function Node:make_node(path)
    use(path)
    return Node
end

--- Returns the last component of the filesystem object's path, such as the directory or file name.
---@return string The final path component, representing either the directory or file name.
function Node:name()
    return ''
end

--- Returns the last component of the filesystem object's path without its extension, i.e., the base name.
---@return string The directory or file name without the file extension.
function Node:basename()
    return ''
end

--- Returns the file extension of the filesystem object, or an empty string if there is no extension.
---@return string The file extension, if present; otherwise, an empty string.
function Node:extension()
    return ''
end

--- Returns the absolute path of the filesystem object.
---@return string The full absolute path of the Node.
function Node:abs_path()
    return ''
end

--- Returns the path of the filesystem object relative to a specified starting Node.
---@param from Node The node from which to calculate the relative path.
---@return string The relative path from the specified starting node.
function Node:path_from(from)
    return ''
end

--- Changes the file extension of the filesystem object. If no extension exists, it adds the new extension; otherwise, it replaces the existing extension.
---@param new_extension string The new file extension, without the `.` prefix.
function Node:change_ext(new_extension)
end

--- Checks if the filesystem object exists and is a directory.
---@return boolean `true` if the node represents an existing directory; otherwise, `false`.
function Node:is_dir()
    return false
end

--- Checks if the filesystem object exists and is a file.
---@return boolean `true` if the node represents an existing file; otherwise, `false`.
function Node:is_file()
    return false
end

--- Resolves a symbolic link to find the target filesystem object, if it exists. Only dereferences the last component of the path.
---@return Node A new node representing the resolved target filesystem object.
function Node:read_link()
    return self
end

--- Canonicalizes the filesystem path, resolving any symbolic links along the entire path to the target object.
---@return Node A new node representing the fully resolved target filesystem object.
function Node:canonicalize()
    return self
end

--- Deletes the file represented by the node. Raises an error if deletion fails.
function Node:delete()
end

--- Deletes the file represented by the node, ignoring any errors if the operation fails.
function Node:try_delete()
end

--- Reads the contents of the file represented by the node as a raw string, without processing encoding.
---@return string The raw content of the file.
function Node:read()
    return ''
end

--- Writes the specified string content to the file represented by the node, without processing encoding.
---@param content string The raw content to write to the file.
function Node:write(content)
end
