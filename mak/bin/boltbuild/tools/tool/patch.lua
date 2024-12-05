---@type Context
local context = ...
context:load_tool('internal/bolt')

Bolt.Patch = {}

--- Patches a source file or directory using a specified diff file or list of diff files.
--- This function declares a patch task in the generator, sets the environment variables for the patch process,
--- and optionally strips a number of leading directories and uses the source file or directory directly.
--- If the source is a directory, it is used as the reference to find the files mentioned in the diff,
--- using `strip` as the number of directories to strip from the diff specification.
---
--- @param generator Generator The generator object that declares the patch task.
--- @param diff Node|Node[] The diff file(s) to apply to the source file or directory.
--- @param source Node The source file or directory to be patched.
--- @param target Node The target file or directory after patching.
--- @param strip number? The number of leading directories to strip in the diff file.
function Bolt.Patch.patch(generator, diff, source, target, strip)
    strip = strip or 1
    if type(diff) ~= 'table' then
        diff = { diff }
    end
    generator:declare_task('patch', { source, table.unpack(diff) }, { target })
    generator.env.PATCH_STRIP = strip
end
